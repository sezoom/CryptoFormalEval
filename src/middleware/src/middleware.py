import subprocess
import sys
import threading
import requests
import re
import socket
import os
from readtraces import read_traces

from dotenv import load_dotenv

if not load_dotenv(dotenv_path=  "./../../", override=True ):
    print(".env file not found")

# Hard-coded fallback values
DEFAULT_TAMARIN_COMMAND = 'tamarin-prover'
DEFAULT_TIMER_DURATION = 200
DEFAULT_URL = 'http://127.0.0.1:3001/thy/trace/1/overview/help'
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 3003
DEFAULT_OUTPUT_DIR = './Agent_execution'
DEFAULT_TRACES_PATH = './Agent_execution/traces.json'

# Helper function to fetch environment variable or raise an exception if not found and no default is provided
def get_env_var(var_name, default=None, required=False):
    value = os.getenv(var_name)
    if value is None:
        if required and default is None:
            raise EnvironmentError(f"Missing required environment variable: {var_name}")
        value = default
    return value

# Fetch environment variables with fallback to hard-coded values
tamarin_command = get_env_var('TAMARIN_COMMAND', DEFAULT_TAMARIN_COMMAND, required=True)
timer_duration = int(get_env_var('MAX_TIMER_DURATION_EACH_COMMAND', DEFAULT_TIMER_DURATION, required=True))
url = get_env_var('URL', DEFAULT_URL, required=True)
host = get_env_var('HOST', DEFAULT_HOST, required=True)
port = int(get_env_var('PORT', DEFAULT_PORT, required=True))
output_dir = get_env_var('OUTPUT_DIR', DEFAULT_OUTPUT_DIR, required=True)
traces_path = get_env_var('TRACES_PATH', DEFAULT_TRACES_PATH, required=True)



# tamarin_command = os.getenv('TAMARIN_COMMAND')
# timer_duration = int(os.getenv('MAX_TIMER_DURATION_EACH_COMMAND'))
# url = os.getenv('URL')
# host = os.getenv('HOST')
# port = int(os.getenv('PORT'))
# output_dir = os.getenv('OUTPUT_DIR')
# traces_path = os.getenv('TRACES_PATH')
# env_path = os.getenv('PATH')

env_path = os.getenv('PATH')
if env_path:
    os.environ['PATH'] = env_path + ':' + os.environ.get('PATH', '')
    print("Updated PATH:", os.environ['PATH'])
else:
    print("PATH not found in .env")

def read_output(process):
    for line in iter(process.stdout.readline, ''):
        print(line.strip())

def kill_process(process):
    try:
        process.terminate()
        print("Process terminated due to timeout.")
    except Exception as e:
        print(f"Error terminating process: {e}")

# Use a flag to signal to the thread that it must terminate gracefully
exit_flag = threading.Event()
def manual_search() :
    # Open a listening socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        # Keep listening for incoming connections until the exit flag is set.
        # There will be a separated connection for each oracle call from Tamarin.
        while not exit_flag.is_set() :
            conn, _ = s.accept()
            with conn:
                # Retrieve the list of goals
                data = conn.recv(1024)
                # If no data is received, listen to further incoming connections
                if not data : continue
                # Otherwise, print the list of goals to choose from
                print(data.decode())
                # Save the agent's choice
                choice = input(">>> ")
                # Send the choice back to the oracle and terminate the connection
                conn.sendall(choice.encode())

def main():
    args = sys.argv[1:]

    # Check that the first command-line argument provides the path to a file
    if args == [] or (not os.path.exists(args[0])) or (not os.path.isfile(args[0])):
        print("Error: no input file detected")
        exit(1)

    # Ensure that the first command contains a valid Tamarin theory
    input_file = args[0]
    command = [ tamarin_command, input_file, "--parse-only" ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # If Tamarin produces a syntax error while parsing, print it and terminate the program
    stdout, stderr = process.communicate()
    if process.returncode != 0 :
        print(stderr)
        exit(2)

    # If we need to check partial deconstructions, we have to parse the web interface
    if "--check-partial-deconstructions" in args :
        args.remove("--check-partial-deconstructions")
        # Execute Tamarin in interactive mode to have access to the web interface
        args.insert(0, "interactive")
        command = [tamarin_command] + args
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Tamarin may not terminate during precoumputation, so a timer must be set to ensure avoiding looping indefinitely
        timer = threading.Timer(timer_duration, kill_process, [process])
        timer.start()
        try:
            # Send a connection request to the server only after the initial saturation phase
            it = iter(process.stdout.readline, '')
            while True :
                line = next(it).strip()
                # When the server is ready it automatically checks for PNG support and logs it to the command line
                if "Application launched" in line : break
            # Send a GET request to the Web interface to parse (this begins the precomputation phase)
            response = requests.get(url)
            # If a response is received, the Tamarin process can be terminated
            process.terminate()
            # Search for the result via regex matching
            pattern = r'<a class="internal-link" href="/thy/trace/1/main/cases/refined/0/0"><strong>Refined sources </strong> \(\d+ cases, (deconstructions complete|(\d+) partial deconstructions left)\)</a><br/>'
            match = re.search(pattern, response.text)
            if match: print(match[1])
            else:
                print("Error: No match found in the HTML source. Something has gone wrong with the interactive mode.")
                exit(3)
            process.wait()
        except Exception as e:
            # If the timer runs out, the Tamarin process terminates automatically, abruptly terminating the connection began by requests.get(url). This will lead to a connection error.
            print(f"Error: Precomputation did not terminate. More information: {e}")
            exit(4)
        finally:
            timer.cancel()
            exit(0)

    else :
        # This branch requires at least one lemma to prove
        lemmas = re.findall(r'lemma\s*(?:\[[^\]]*\]\s*)?([^\s\[\]]+)(?:\s*\[[^\]]*\])?\s*:', stdout)
        if lemmas == [] :
            print("Error: No lemma to prove")
            exit(5)

        # Manual guiding works by re-routing the inputs of the custom oracle to a separate thread of this program via a socket (and vice-versa for the choices)
        if "--manual-guide" in args :
            args.remove("--manual-guide")
            args += [ "--prove", f"--Output={output_dir}", f"--output-json={traces_path}" ]

            # First of all, it is necessary to specify that the custom oracle must be used for guiding: we make a temporary copy of the theory file and include the flag for using the oracle. The temporary copy will be deleted at the end to avoid junk files.
            with open(args[0], "r") as f :
                data = f.read()
            idx = data.find("begin")
            data = data[:idx+5] + '\nheuristic: o "manualguide.py"\n' + data[idx+5:]
            with open("temp.spthy", "w") as f :
                f.write(data)
            args.pop(0)
            args.insert(0, "temp.spthy")

            # Start a listening socket on a separated thread. The synchronization with the main timer is done via a event flag.
            server_thread = threading.Thread(target=manual_search)
            server_thread.start()

            # Execute Tamarin on the temporary file
            command = [tamarin_command] + args
            tamarin_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            tamarin_thread = threading.Thread(target=read_output, args=(tamarin_process,))
            tamarin_thread.start()

            # Start the timer to avoid incourring into non-termination
            timer = threading.Timer(timer_duration, kill_process, [tamarin_process])
            try:
                timer.start()
                tamarin_process.wait()
            finally:
                timer.cancel()
                tamarin_thread.join()
                # When the Tamarin process is terminated, it is important to close the socket and terminate the thread
                exit_flag.set()
                server_thread.join()
                # Finally, remove the temporary file
                os.remove("temp.spthy")

        # Standard execution of the proof search via heuristics
        else :
            args += [ "--prove", f"--Output={output_dir}", f"--output-json={traces_path}" ]

            # Execute Tamarin on the provided input
            command = [ tamarin_command ] + args
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            thread = threading.Thread(target=read_output, args=(process,))
            thread.start()

            # Start a timer to avoid non-termination
            timer = threading.Timer(timer_duration, kill_process, [process])
            try:
                timer.start()
                process.wait()
            finally:
                timer.cancel()
                thread.join()

        # Check if Tamarin has proved any property
        analyzed_path = f"{args[0][:-6]}_analyzed.spthy"
        # If not, something must have gone wrong when trying to prove (e.g.: welformedness errors on the formulae)
        if not os.path.exists(analyzed_path) :
            print("Error: Something went wrong during the analysis")
            exit(6)
        # Check if there are any warnings in the theory
        with open(analyzed_path, "r") as f :
            analyzed = f.read()
        pattern = r'/\*\nWARNING.*?\*/'
        warnings = re.findall(pattern, analyzed, re.DOTALL)
        # If any, print them before the results
        if warnings : print(warnings[0])

        # Check if a valid trace was found
        with open(traces_path, "r") as f :
            data = f.read()
            # If not, then there must have been some mistake in the formalization
            if len(data) == 0 :
                print("Error: No attack trace found")
                exit(7)

        # Otherwise, print the attacks as topological sorts of the traces
        ordered_traces = read_traces(traces_path, lemmas)
        for attack in ordered_traces :
            print(f"\n{78*'='}\n")
            print(f"\nAttack trace for {attack}:\n")
            for node in ordered_traces[attack] : print(node)
            print(f"\n{78*'='}\n")
        exit(0)

if __name__ == "__main__":
    main()