# CryptoFormalEval
Evaluation + Agent

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/
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
    Follow instructions in

6. Compile ./src/formalizer
   Follow instructions in ./src/formalizer/README

7. Make sure that both the Tamarin prover and the formalizer works correctly. You can test them using the following commands:
    ```bash
    ```
    and check if the file outputs are produced.

8. Modify the `.env.example` file by adding API keys and the `$PATH`. You can print using 
    ```bash
   echo $PATH
    ```
   and then copy it in the  `.env` file.

## Usage

Explain how to run and use the project, including examples if applicable.

Example:
```bash
python main.py
```

Or if you're using a specific framework:
```bash
flask run
```

### Additional Commands

If there are any other commands or options, list them here.

## Features

- Feature 1
- Feature 2
- Feature 3

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements


