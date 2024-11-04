This repository contains the LLM-based Agent for the project. The README.md file serves as an introduction and provides an overview of the repository's contents and usage instructions.
Main files:
- `main.py`: is the executable file, containing the hyperparameter set-up to feed the agent with an input protocol in `dataset/Input/`.
- `main_print_interactions.py`: contains the code to print, as plain text or tabulate form, the LLM interaction based on run ID (the folder name in `agent_executions`) and task number (from 1 to 6). File outputs are created in `history_run/`. 
- `.env`: contains the required API keys, the PATH variable (fundamental to include Tamarin) and other technical information required by the middleware to interact with Tamarin.
- `agent.ipynb`: contains the LLM-based Agent class, the whole implementation of the agent.


Folders:
- agent_execution/: contains the files produced in each agent's execution.
- history_run/: stores all the information of past agent's execution in a json file. Contains the outfile files produced by `main_print_interactions.py`
- prompts/: contains the prompts and examples used to guide the LLM-based Agent. It also contains some input examples.
- formalizer/: contains the tool (Anb -> Tamarin syntax converter), that should be compiled following formalizer/README instructions.
- middleware/: contains the code to interact with Tamarin.

