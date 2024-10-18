This repository contains the LLM-based Agent for the project. It includes code and running examples. The README.md file serves as an introduction and provides an overview of the repository's contents and usage instructions. For the moment, it's not user friendly, but it will be updated soon.
Main file:
- `Agent.ipynb`: Contains the LLM-based Agent class and the main to be executed.
- `main_print_interactions.py`: Contains the code to print, as plain text or tabulate form, the LLM interaction based on run ID (last folder name in `agent_executions` and task number).
- `.env`: Should contain API keys, the PATH variable (which includes the Tamarin executable) and other technical information required by the middleware to interact with Tamarin.
- 

Other files:
- agent_execution/id_run/: Contains stored examples of the agent's execution.
- history_run/: Stores all the information of past agent's execution in a json file. Contains the outfile files produced by `main_print_interactions.py`
- prompts/: Contains the prompts, examples used to guide the LLM-based Agent and some input example tests.
- formalizer/: Contains the tool, that should be compiled following formalizer/README instructions, to transform .anb files to .spthy Tamarin syntax.

