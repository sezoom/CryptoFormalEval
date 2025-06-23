import os
import subprocess
import tiktoken
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from prompts.Examples import *
from prompts.Systems import *
from prompts.Tests import *
from history_run.json_store import *


load_dotenv(override=True)
env_path = os.getenv('PATH')

if env_path:
    os.environ['PATH'] = env_path + ':' + os.environ.get('PATH', '')
    # print("Updated PATH:", os.environ['PATH'])
else:
    print("PATH for Tamarin execution not found in .env")

# Update model config to try a new core LLM
MODEL_CONFIGS = {
    "gpt-4-turbo": {"max_tokens": 128000, "up_training_date": "Dec 2023"},
    "gpt-4o": {"max_tokens": 128000, "up_training_date": "Oct 2023"},
    "gpt-3.5-turbo-0125": {"max_tokens": 16384, "up_training_date": "Sep 2021"},
    "gpt-4o-mini": {"max_tokens": 16384, "up_training_date": "Oct 2023"},
    "claude-3-5-sonnet-20240620": {"max_tokens": 200000, "up_training_date": "Apr 2024"},
    "claude-3-haiku-20240307": {"max_tokens": 200000, "up_training_date": "Aug 2023"},
    "claude-3-opus-20240229": {"max_tokens": 200000, "up_training_date": "Aug 2023"},
    "o1-preview-2024-09-12": {"max_tokens": 128000, "up_training_date": "Oct 2023"}
}

class Agent:
    def __init__(self, model_name='gpt-3.5-turbo-0125', Selected_Test="", max_api_calls=15, initial_task_number=1, user_interactive=False,
                 maximum_number_of_repetition=3, test_number=3, max_time_command_execution= int(os.getenv('MAX_TIMER_DURATION_EACH_COMMAND'))):

        self.max_api_calls = max_api_calls
        self.user_interactive = user_interactive
        self.task_number = initial_task_number-1  # Default 0
        self.timeout = max_time_command_execution
        self.max_repeated_task= maximum_number_of_repetition
        self.memory = {}
        self.model_name = model_name
        self.info = {"3": "", "4": "", "5": ""}  # To structure extra info tag in the prompt.
        self.count_input_token=0
        self.count_output_token=0

        # Update initialization to try a new core LLM
        """Initialize the appropriate model based on the model name."""
        model_config = MODEL_CONFIGS.get(self.model_name)
        if model_config:
            self.max_tokens = model_config["max_tokens"]
            self.up_training_date = model_config["up_training_date"]
            if "gpt" in self.model_name:
                self.llm = ChatOpenAI(model_name=self.model_name, temperature=0.1, verbose=True)
            elif "claude" in self.model_name:
                self.llm = ChatAnthropic(model_name=self.model_name, temperature=0.1, verbose=True)
            elif "o1" in self.model_name:
                self.llm = ChatOpenAI(model_name=self.model_name, temperature=1, verbose=True)
        else:
            raise ValueError("Model name not found!")

        #self.prompt = ChatPromptTemplate.from_messages([("system", SystemPrompt1)])
        self.prompt = PromptTemplate.from_template("{SystemPrompt}")
        self.chain = self.prompt | self.llm | StrOutputParser()
        self.model_info = f"Model: {self.model_name}, Temperature: {self.llm.temperature}, Max Tokens: {self.max_tokens}"

        # To handle the executions of the agent's commands
        self.ID_run = 0
        self.run_id_dir = ""
        self.agent_dir = os.path.join(os.getcwd(), 'agent_execution')

        # Loading prompts
        self.tasklist = [[CreateProtocolFile1, CreateProtocolFile2], [FormalizingTool1, FormalizingTool2], [ConfrontAndFix1, ConfrontAndFix2], [MyAttackTrace1, MyAttackTrace2], [TamarinInteraction1, TamarinInteraction2],
                         [TranslateTrace1, TranslateTrace2]]
        self.examplelist = [
            [Example1_CreateProtocolFile, Example2_CreateProtocolFile, Example3_CreateProtocolFile, Example4_CreateProtocolFile, Example5_CreateProtocolFile],
            [Example1_FormalizingTool, Example2_FormalizingTool, Example3_FormalizingTool, Example4_FormalizingTool, Example5_FormalizingTool],
            [Example1_ConfrontAndFix, Example2_ConfrontAndFix, Example3_ConfrontAndFix],
            [Example1_MyAttackTrace, Example2_MyAttackTrace, Example3_MyAttackTrace],
            [],
            [Example1_TranslateTrace, Example2_TranslateTrace, Example3_TranslateTrace],
        ]
        self.testlist = [Test1, Test2, Test3, Test4]
        self.Extra_Info= ExtraInfo1 # or ExtraInfo2?
        self.SystemPrompt=SystemPrompt2

        if Selected_Test:
            self.test=Selected_Test
        else:
            self.test = self.testlist[test_number - 1]

    @staticmethod
    def __is_safe_command(command) -> bool:
        # Check for dangerous patterns
        if 'cd ' in command or '../' in command or command.startswith('/'):
            print("command not safe, it contains cd or ../ ")
            return False
        # Remove the possibility of changing environment variables
        if 'export ' in command:
            print("command not safe, it contains export  ")
            return False
        return True

    def __execute_safe_command(self, command: str) -> str:
        """Block cd commands and read/modify out of the agent directory, changing environment vars."""
        if self.__is_safe_command(command=command):
                try:
                    print(command)
                    env = os.environ.copy()
                    # Modify env if necessary
                    result=subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                            text=True, env=env, timeout=self.timeout)
                    print(result.stdout)
                    return result.stdout
                except subprocess.CalledProcessError as e:
                    # Combine stdout and stderr for better diagnosis
                    error_message = f"{e.stderr} {e.stdout}" if e.stderr or e.stdout else "No error message available"
                    print(f"Command '{command}' failed with error: {error_message}")
                    return f"Command '{command}' failed with error: {error_message}"
                except subprocess.TimeoutExpired:
                    print("The command took too long and was terminated.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
        else:
            return f"Command '{command}' is not allowed."

    @staticmethod
    def __map_output_to_command(output: str) -> list:
        """Extracts shell commands from the given output string.

        This function searches the output string for blocks of text marked as shell commands
        (delimited by ```shell and ```), and then extracts the actual commands listed within
        those blocks which must be written after "execute:". It returns a list of these commands.

        Args:
            output (str): The output string containing shell command blocks.

        Returns:
            list: A list of extracted shell commands.
        """
        commands = []
        start = 0
        #
        while "```shell" in output[start:]:
            shell_start = output.find("```shell", start) + len("```shell")
            shell_end = output.find("```", shell_start)
            shell_block = output[shell_start:shell_end].strip()
            execute_start = 0
            while "execute:" in shell_block[execute_start:]:
                exec_start_idx = shell_block.find("execute:", execute_start) + len("execute:")
                exec_end_idx = shell_block.find("execute:", exec_start_idx)
                if exec_end_idx == -1:
                    exec_end_idx = len(shell_block)
                command = shell_block[exec_start_idx:exec_end_idx].strip()
                commands.append(command)
                execute_start = exec_end_idx
            start = shell_end + len("```")
        return commands

    @staticmethod
    def __map_output_to_summary(output: str) -> str:
        """ Extract the summary delimited by ```summary and ``` and returns it.
            Args:
                output (str): The output string of the LLM
            Returns:
                summaries (str): A string containing the summary

        """
        summaries = ""
        start = 0
        while "```summary" in output[start:]:
            summary_start = output.find("```summary", start) + len("```summary")
            summary_end = output.find("```", summary_start)
            # If no closing marker is found, break the loop to avoid infinite looping
            if summary_end == -1:
                break
            summaries += output[summary_start:summary_end].strip()
            start = summary_end + len("```")
        return summaries


    def __create_new_execution_dir(self) -> str:
        """Create a new directory for the execution of the agent. Changes self.ID_run to the new ID RUN"""
        if not os.path.exists(self.agent_dir):
            os.makedirs(self.agent_dir)

        existing_dirs = [int(name) for name in os.listdir(self.agent_dir) if name.isdigit()]
        self.ID_run = max(existing_dirs, default=0) + 1
        self.run_id_dir = os.path.join(self.agent_dir, str(self.ID_run))
        os.makedirs(self.run_id_dir)
        return self.run_id_dir

    def __task_info_3(self) -> str:
        """Handles extra_info in task 3

        This function reads the contents of the auto-generated and LLM-generated protocol
        and property files and formats them into a string.
        The string contains 'auto_protocol_and_property.spthy' and 'my_protocol_and_property.spthy' file's contents.

        Returns:
            str: A formatted string containing 'auto_protocol_and_property.spthy' and 'my_protocol_and_property.spthy'.
        """
        result = "## This is the automatic protocol generation, content of the auto_protocol_and_property.spthy file: \n"
        result += subprocess.run(
            ['cat', os.path.join(os.getcwd(), 'agent_execution', 'auto_protocol_and_property.spthy')],
            capture_output=True, text=True).stdout
        result += "\n\n## This is your protocol and property generation, content of the my_protocol_and_property.spthy file: \n"
        result += subprocess.run(
            ['cat', os.path.join(os.getcwd(), 'agent_execution', 'my_protocol_and_property.spthy')],
            capture_output=True, text=True).stdout
        self.info["3"] = result.strip()
        return repr("## This is the AnB input:\n" + str(self.test) + self.info["3"])

    def __move_files(self) -> bool:
        """Moves files from the agent's execution directory to a new run-specific directory.

        This function checks if the source and destination directories exist, creates the
        destination directory if it doesn't, and moves all files from the source directory
        to the destination directory using the `mv` command.

        Raises:
            ValueError: If the source directory does not exist.

        Returns:
            bool: True if the files are moved successfully.
        """
        if not os.path.exists(self.agent_dir):
            raise ValueError(f"Source directory {self.agent_dir} does not exist.")
        if not os.path.exists(self.run_id_dir):
            os.makedirs(self.run_id_dir)

        # List all files in the source directory
        files = os.listdir(self.agent_dir)
        print(self.agent_dir, self.run_id_dir, files)
        for file in files:
            # Move only files using subprocess
            if os.path.isfile(os.path.join(self.agent_dir, file)):
                subprocess.run(['mv', os.path.join(self.agent_dir, file), self.run_id_dir])
        return True

    def __format_next_step(self, extra_info_commands="", extra_info_feedback="", task_repeated=1):
        """Formats the next step prompt based on the current task number and extra information.

        Args:
            extra_info_feedback (str): Additional information to include in the prompt. Defaults to "".
            extra_info_commands (str): Commands
            task_repeated (int): used to select the prompt

        Returns:
            str: The formatted next step prompt.
        """

        # Select next step prompt
        next_step = self.tasklist[self.task_number - 1][(task_repeated-1) % len(self.tasklist[self.task_number - 1])]

        # Add extra infos if a feedback is available, empty otherwise
        if extra_info_feedback:
            extra_info = repr(self.Extra_Info.format(shell_executed=extra_info_commands, shell_feedback=extra_info_feedback))
        else:
            extra_info = repr("")

        if self.task_number == 1 or self.task_number == 2:
            try:
                # To allow prompt system to use graphs parenthesis before inserting strings: {}
                index1 = next_step.find("{Extra_Info}")
                len1=len(r"""{Extra_Info}""")
                aux1 = next_step[index1: index1 + len1].format(
                    Extra_Info= extra_info,
                )

                index2= next_step.find("{Example}")
                aux2 = next_step[index2:].format(
                Example = "\n".join(self.examplelist[self.task_number - 1]),
                Task = self.test
                )
                return next_step[:index1] + aux1 + next_step[index1+len1 : index2] + aux2

            except Exception as e:
                print("Error in formatting next step: ", e)
                print("Task number: ", self.task_number)

        if self.task_number == 3:
            if not self.examplelist[self.task_number - 1]:
                print("No examples in task: ", self.task_number)
                return next_step.format(Example="", Extra_Info= extra_info, Task=self.__task_info_3())
            else:
                return next_step.format(Example="\n".join(self.examplelist[self.task_number - 1]), Extra_Info= extra_info,
                                        Task=self.__task_info_3())
        if self.task_number == 4:
            # TODO Future improving: if the prove is correct just stop it and assign positive points. Use the sandbox.
            return next_step.format(Example="\n".join(self.examplelist[self.task_number - 1]), Extra_Info= extra_info,
                                    Task=self.test)
        if self.task_number == 5:
            # Test is content of final_protocol_and_property.spthy
            try:
                self.test = subprocess.run(
                    ['cat', os.path.join(os.getcwd(), 'agent_execution', 'final_protocol_and_property.spthy')],
                    capture_output=True, text=True).stdout
            except Exception as e:
                print("Error in reading final_protocol_and_property.spthy: ", e)

            return next_step.format(Extra_Info= extra_info, Task= "Here is the content of the final_protocol_and_property.spthy file, used in the previous Tamarin execution: \n" + self.test)

        if self.task_number == 6:
            # Test is content of agent_execution/tamarintrace.txt and agent_execution/MyTraces.txt
            try:
                tamarin_trace: str = subprocess.run(['cat', os.path.join(os.getcwd(), 'agent_execution', 'tamarintrace.txt')],
                                              capture_output=True, text=True).stdout
                llm_trace: str = subprocess.run(['cat', os.path.join(os.getcwd(), 'agent_execution', 'MyTraces.txt')],
                                          capture_output=True, text=True).stdout
                self.test = f"This the LLM-generated attack trace: {llm_trace} \n This is the attack produced by Tamarin: {tamarin_trace}\n"
            except Exception as e:
                print("Error in reading tamarintrace.txt or MyTraces.txt: ", e)

            return next_step.format(Example="\n".join(self.examplelist[self.task_number - 1]), Extra_Info= extra_info,
                                    Task=self.test)
        return next_step

    @staticmethod
    def count_tokens(text: str, model_name="gpt-3.5-turbo-0125"): #Claude doesn't have a token count easily available
        # Get the tokenizer for the given OpenAI model
        encoding = tiktoken.encoding_for_model(model_name)

        # Tokenize the input text and count the number of tokens
        tokens = encoding.encode(text)
        return len(tokens)

    def build_next_step_prompt(self, all_llm_summary: str, extra_info_commands: str, extra_info_feedback: str, task_repeated = 1) -> str:
        """Adjusts the prompt to fit within the maximum token limit.

        This function repeatedly formats the prompt and checks its token length. If the prompt
        exceeds the maximum token limit, examples are removed from the prompt until it fits
        within the limit. The final adjusted prompt is then returned.

        Args:
            all_llm_summary (str): The summary of all LLM outputs so far.
            extra_info_commands (str): Commands executed
            extra_info_feedback (str): the extra information.
            task_repeated (int): used to select a prompt of same task

        Returns:
            str: The adjusted prompt that fits within the maximum token limit.
        """

        next_step = self.__format_next_step(extra_info_commands, extra_info_feedback, task_repeated)
        complete_prompt = self.SystemPrompt.format(summary=all_llm_summary, next_step=next_step) # or SystemPrompt2
        # remove example from the prompt if the prompt is too long
        num_token= self.count_tokens(complete_prompt)
        self.count_input_token+=num_token
        while num_token > self.max_tokens:
            # print("Prompt tokens: ", self.count_tokens(complete_prompt))
            # print("Max tokens: ", self.max_tokens)
            try:
                self.examplelist[self.task_number - 1].pop()
                print("Removed example from the prompt.")
                print("\n Remaining examples: ", len(self.examplelist[self.task_number - 1]))
            except Exception as e:
                print("Context window filled by summaries and extra infos: ", e)

            next_step = self.__format_next_step(extra_info_commands, extra_info_feedback, task_repeated)
        return next_step


    @staticmethod
    def convert_number_to_tasknumber(number: str) -> str:
        # Convert string to integer, if possible
        try:
            number = int(number)
        except ValueError:
            return "Invalid input, please provide a number"

        if number < 1 or number > 6:
            return "Invalid number"

        task_mapping = {
            1: "1.1",
            2: "1.2",
            3: "1.3",
            4: "2.1",
            5: "2.2",
            6: "2.3"
        }

        return task_mapping.get(number, "Invalid number")

    def interact(self, all_llm_output="", all_llm_summary="") -> list:
        """
            Main function
        """
        # Initialization
        error_tag = False
        task_repeated = 0
        chain_count = 0
        shell_feedback = ""
        executed_commands_list=[]
        self.run_id_dir = self.__create_new_execution_dir()  # Run ID


        # Pipeline
        while chain_count < self.max_api_calls and self.task_number < len(self.tasklist):
            chain_count += 1
            print(f"Number of LLM calls: {chain_count}")


            if (("**Next step**" in all_llm_output or "**Next step:**" in all_llm_output  or all_llm_output == "") and not error_tag) or task_repeated >= self.max_repeated_task:  # Repeat or go ahead?
                # Go ahead
                self.task_number += 1
                shell_feedback = ""
                executed_commands_list=[]
                task_repeated = 0

                # Automatic executions before starting, just once!
                if self.task_number == 5:
                    command = "python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy"
                    shell_feedback = self.__execute_safe_command(command)
                    executed_commands_list.append(command)


            else:
                # Repeat
                task_repeated += 1
                print(f"Repeat the task {self.task_number} for the {task_repeated}^th time.")

            # Build the next step prompt
            next_step = self.build_next_step_prompt(all_llm_summary, "\n".join(executed_commands_list), shell_feedback, task_repeated)

            complete_prompt = self.SystemPrompt.format(summary=all_llm_summary, next_step=next_step)

            # API CALL
            # response = self.chain.invoke({"summary": all_llm_summary, "next_step": next_step})
            response= self.chain.invoke({'SystemPrompt': self.SystemPrompt.format( summary=all_llm_summary, next_step= next_step)})
            self.count_output_token+=self.count_tokens(response)

            # Got response! Let's execute commands and prepare feedback for the next task
            shell_feedback=""
            executed_commands_list=[]
            # Command execution
            shell_command_list = self.__map_output_to_command(response)
            for command in shell_command_list:
                shell_feedback +=  self.__execute_safe_command(command) + "\n"
                executed_commands_list.append(command)

            # Automatic executions after LLM call, every time it's repeated
            if self.task_number == 3:
                # Execute Tamarin for syntax feedback
                command = "python3 middleware/src/middleware.py agent_execution/final_protocol_and_property.spthy"
                shell_feedback+= self.__execute_safe_command(command)
                executed_commands_list.append(command)


            if self.task_number == 2:
                # Execution of the formalizer .anb -> .spthy
                command = "formalizer/./anb agent_execution/protocol.anb -o agent_execution/auto_protocol_and_property.spthy"
                shell_feedback += self.__execute_safe_command(command)
                executed_commands_list.append(command)


            error_tag = 'error' in shell_feedback or 'The following well-formedness checks failed' in shell_feedback # TRUE iff error/failed in shell feedback

            all_llm_output += response + "\n"
            all_llm_summary += "Task number "+ self.convert_number_to_tasknumber(str(self.task_number)) + ": "+self.__map_output_to_summary(response) + "\n"

            # Storing infos json logger
            time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger = InteractionLogger()
            logger.store_interaction(self.ID_run, self.task_number, time_stamp, self.model_info,
                                     complete_prompt.encode('utf-8').decode('unicode_escape').replace(r"\(", "("), response, shell_feedback)
            # Storing infos on database
            # store_interaction_db(self.db_path, self.ID_run, self.model_info, "\n".join(executed_commands_list), shell_feedback,
            #                      complete_prompt.encode('utf-8').decode('unicode_escape').replace(r"\(", "("), response)

            # Only if User interactive mode on
            if self.user_interactive:
                print(logger.display_interactions(id_run=self.ID_run, task_number=self.task_number))
                user_decision = input(
                    "Do you want to proceed with the next steps or modify the shell commands? (proceed/modify/quit): ").strip().lower()
                if user_decision == "modify":
                    # Allow user to input new commands
                    shell_command_list = []
                    while True:
                        user_command = input("Enter shell command (or 'done' to finish): ").strip()
                        if user_command.lower() == "done":
                            break
                        shell_command_list.append(user_command)
                    print("Shell feedback: ", self.__execute_safe_command(shell_command_list[0])) # TODO

                elif user_decision == "quit":
                    self.user_interactive = False
                elif user_decision == "proceed":
                    pass
                else:
                    print("Invalid input. Proceeding with the next steps.")
                    pass


        print("Input Token Count: ", self.count_input_token)
        print("Output Token Count: ", self.count_output_token)
        self.__move_files()  # Move all files to the id folder execution
        return [all_llm_output, self.run_id_dir]


def load_dataset_input(input_id: int, path_input= os.path.join(os.getcwd(), 'dataset', 'Input')):
    """
    This function loads a task from a specified .txt file based on the input_id.

    Args:
        input_id (int): Identifier to determine which numbered text file to load (1 to 15).
        path_input (str): Path to the directory containing the text files.

    Returns:
        str: Contents of the specified text file.
    """
    # Construct the file name based on the input_id (e.g., '1.txt', '2.txt', etc.)
    file_name = f"{input_id}.txt"
    full_path = os.path.join(path_input, file_name)

    # Check if the file exists
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"The file {file_name} was not found in the directory {path_input}.")

    # Open and read the content of the text file
    with open(full_path, 'r') as file:
        content = file.read()

    return content


# Example usage
# if __name__ == "__main__":
#
#         agent = Agent(max_api_calls=2, initial_task_number=1, test_number=3 , maximum_number_of_repetition=3, model_name='gpt-4o', user_interactive=False)
#         outputs, run_id_dir = agent.interact()
#         print("Completed!")

