# CryptoFormalEval: Automated Benchmark for LLM Vulnerability Detection in Cryptographic Protocols

## Introduction

Cryptographic protocols are essential to the security of modern digital infrastructures, but they are frequently deployed without undergoing formal verification, exposing systems to potential hidden vulnerabilities. Although formal verification methods are rigorous and effective, they are often complex and time-intensive, making them challenging to apply consistently in real-world scenarios. This project addresses this gap by introducing an automated benchmark designed to evaluate the capability of Large Language Models (LLMs) in detecting vulnerabilities in cryptographic protocols.
We present a validated dataset of novel flawed communication protocols, accompanied by an automated validation method for results. In our research, we leverage state-of-the-art prompting and scaffolding techniques for LLMs, combined with Tamarin—a powerful symbolic reasoning tool—to enhance protocol analysis. This integration bridges natural language processing with formal verification, leading to a more efficient and comprehensive assessment of protocol security. Our early results demonstrate the potential of LLMs, augmented by symbolic reasoning, to contribute to defensive cybersecurity applications.

## TL;DR

We introduce a benchmark for testing how well LLMs can find vulnerabilities in cryptographic protocols. By combining LLMs with symbolic reasoning tools like Tamarin, we aim to improve the efficiency and thoroughness of protocol analysis, paving the way for future AI-powered cybersecurity defenses.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Installation

1. Clone and move into the repository:

   ```bash
   git clone git@github.com:Cristian-Curaba/CryptoFormalEval.git
   cd CryptoFormalEval
   ```
2. Create a virtual environment:

   ```bash
   python -m venv LangChain
   ```
3. Activate the virtual environment:

   - **On macOS/Linux:**

     ```bash
     source LangChain/bin/activate
     ```
   - **On Windows:**

     ```bash
     .\LangChain\Scripts\activate
     ```
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
5. Install Tamarin:
   Follow instructions in [Instructions_for_Tamarin_installation.md](Instructions_for_Tamarin_installation.md))
6. Compile ./src/formalizer
   Follow instructions in [src/formalizer/README](src/formalizer/README)
7. Modify the `.env.example` file by adding API keys and the `$PATH` global variable (to execute Tamarin).

## Usage

Run the main file:

```bash
cd src
python main.py
```

To explore the produced outputs, you can check the [src/agent_execution](src/agent_execution) folder.
To further analysis, run the [src/main_print_interactions.py](src/main_print_interactions.py) file (change the `id_run`) and inspect `src/history_run` folder.
You can change run parameter in the `main.py` file to test different protocols, limits, LLMs.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.

## Inspecting Dataset and Results

In order to preserve the dataset from LLM memorization, we release the password decrypt the [dataset.zip](dataset.zip) file upon request, and under the terms outlined in the [LICENSE](LICENSE).

## License

This project is licensed under the GNU GENERAL PUBLIC License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

This research was made possible through the generous support of [Apart Research](https://www.apartresearch.com/), which provided both expert research guidelines and access to APIs.
Their resources and guidance have been instrumental in shaping the direction and success of this work.
We also extend our gratitude to our main research advisor, Natalia  for their expertise, mentorship, and insightful feedback throughout the project.
