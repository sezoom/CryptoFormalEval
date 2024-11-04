from agent import *
if __name__ == "__main__":

        agent = Agent(max_api_calls = 2, initial_task_number=1, test_number=3 , maximum_number_of_repetition=3, model_name='gpt-3.5-turbo-0125', user_interactive=False)
        outputs, run_id_dir = agent.interact()
        print("Completed!")

# list of model_name:
    # 'gpt-4-turbo'
    # 'gpt-4o'
    # 'gpt-3.5-turbo-0125'
    # claude-3-5-sonnet-20240620
    # claude-3-opus-20240229"
    # claude-3-haiku-20240307
    # o1-preview-2024-09-12
