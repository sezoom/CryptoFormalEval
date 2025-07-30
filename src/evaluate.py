import datetime

from agent import *

def getInput(file):
    with open(file) as f:
        return f.read()

if __name__ == "__main__":
    frw=open("outputLog.txt","a+")
    file="dataset/Input/5.txt"
    for modelname in list(MODEL_CONFIGS.keys())[:]:
        print("Evaluating model "+modelname)

        inputAnB=getInput(file)
        agent = Agent(max_api_calls = 2, initial_task_number=1 ,Selected_Test=inputAnB, test_number=1 , maximum_number_of_repetition=3, model_name=modelname, user_interactive=False)
        outputs, run_id_dir = agent.interact()

        frw.write(f"[{datetime.now()}]Completed! {modelname} for {file} in {run_id_dir} \n")


