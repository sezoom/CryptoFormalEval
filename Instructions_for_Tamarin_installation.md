# Tamarin Prover Installation Guide

## Prerequisites

1. Install system dependencies:
   ```bash
   # For Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y build-essential git zlib1g-dev libboost-all-dev curl maude graphviz
   
   # For macOS
   brew install boost maude graphviz ocaml opam
   ```

2. Install Haskell Stack:
   ```bash
   curl -sSL https://get.haskellstack.org/ | sh
   ```

## Installing Tamarin

1. Clone the Tamarin repository:
   ```bash
   git clone https://github.com/tamarin-prover/tamarin-prover.git
   cd tamarin-prover
   ```

2. Checkout the specific revision:
   ```bash
   git checkout ea7b979e436fc32f98369dd4e349fa0c6f1b1efd
   ```

3. Build using Stack:
   ```bash
   make default
   ```
   This process might take 15-30 minutes depending on your system.

4. Install the binary:
   ```bash
   sudo make install
   ```

5. Verify the installation:
   ```bash
   tamarin-prover --version
   ```

## Troubleshooting

- If you encounter memory issues during compilation, try:
  ```bash
  stack build --ghc-options="+RTS -M4G -RTS"
  ```

- If Maude is not found, ensure it's in your PATH:
  ```bash
  which maude
  ```

- For GraphViz issues, verify installation:
  ```bash
  dot -V
  ```

## Running Tamarin

1. Start the interactive mode:
   ```bash
   tamarin-prover interactive .
   ```

2. Access the web interface at:
   ```
   http://localhost:3001
   ```

## System Requirements

- Memory: Minimum 4GB RAM, recommended 8GB+
- Disk Space: At least 2GB free space
- Processor: Multi-core processor recommended
- Operating System: Linux, macOS, or WSL for Windows

## Version Information

- Git revision: ea7b979e436fc32f98369dd4e349fa0c6f1b1efd
- Branch: develop
- Compilation timestamp: 2024-07-07 08:40:09.374915591 UTC