
# Code Refactoring and Conversion Tool

This is a Python-based code refactoring, conversion, and generation tool that uses Gradio for the user interface and the Ollama SDK for language model interactions. The tool provides functionalities to refactor Python code, convert code between frameworks, and generate code based on user input.

## Features

1. **Refactor and Comment Code**: 
   - Refactor Python code for better readability.
   - Add comments explaining the code.
   - Handle exceptions where necessary.

2. **Convert Code**:
   - Convert code from one framework to another (e.g., Next.js to React.js) based on user instructions.
   - Choose from multiple models for the conversion.

3. **Generate Code**:
   - Generate pseudo code from a code request.
   - Convert pseudo code into executable Python code.

## Prerequisites

- Python 3.7 or later
- Virtual environment (recommended)
- Required Python packages: `gradio`, `ollama`
- The Ollama SDK installed and configured

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.ibm.com/girijesh/code-helper 
   cd code-helper
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```

3. **Install the Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Ollama SDK**:
   - Make sure the Ollama SDK is installed and configured on your system.
   - Refer to the [Ollama SDK documentation](https://ollama.ai/docs) for more details.
   - Run the following command to pull models from the Ollama. 
   ```bash
   ollama pull model_name 
   ```

## Usage

1. **Run the Application**:
   ```bash
   python app.py
   ```

2. **Access the Application**:
   - The Gradio interface will launch, and you can open it in your browser to start using the app.

## How to Use

### 1. Refactor and Comment Code
- **Select a Model**: Choose a model from the dropdown list.
- **Paste Your Raw Code**: Enter the Python code you want to refactor.
- **Submit**: Click the "Submit" button to get the refactored code with comments and exception handling.

### 2. Convert Code
- **Select a Model**: Choose a model from the dropdown.
- **Instruction**: Enter the code conversion instructions (e.g., "Convert this Next.js code to React.js").
- **Raw Code**: Paste the code you want to convert.
- **Convert**: Click the "Convert" button to see the converted code.

### 3. Generate Code
- **What Code Do You Want to Write?**: Enter a request for code generation (e.g., "Write a code for implementing quick sort").
- **Generate Pseudo Code**: Click the button to get the pseudo code.
- **Generate Final Code**: Click the button to convert the pseudo code into executable Python code.

## Example Models
- `codestral:latest`
- `granite3-dense:8b`
- `llama3:latest`
- `gemma2:2b`
- `qwen2.5-coder:32b`
- `qwen2.5-coder:14b`

## Notes
- The Ollama SDK is used to communicate with the language models. Ensure that your API keys and configurations are correctly set up.
- If you encounter any issues or need additional models, check the Ollama documentation or your model provider's support page.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contributions
Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

## Contact
For any questions or feedback, please reach out to [girijesh@ibm.com].

--- 

You can customize the sections for installation instructions, dependencies, and contact information as needed!

the capital of israel is now a city full of its residents on their way to the US. At the same time, there are also Palestinians living