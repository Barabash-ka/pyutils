import ollama  
import gradio as gr
from functools import lru_cache

# Function to dynamically fetch models 
def get_available_models():
    # models = ["llama3.1:latest", "codestral:latest", "granite3-dense:8b", "granite3.1-dense:2b", "llama3:latest", "gemma2:2b", 'qwen2.5-coder:32b', 'qwen2.5-coder:14b']
    models = []
    for model in ollama.list().models:
        models.append(model.model)
        # print('Name:', model.model)
        # print('  Size (MB):', f'{(model.size.real / 1024 / 1024):.2f}')
        # if model.details:
        #     print('  Format:', model.details.format)
        #     print('  Family:', model.details.family)
        #     print('  Parameter Size:', model.details.parameter_size)
        #     print('  Quantization Level:', model.details.quantization_level)
        # print('\n')
    return models

# This function processes the raw code
@lru_cache(maxsize=128)  # Cache up to 128 results based on function arguments
def refactor_and_comment(code, selected_model):
    # Construct the prompt for Ollama (Refactor, Comment, Handle exceptions)
    prompt = f"""
    You are an experienced python developer who will refactor the following Python code for better readability, add comments explaining the code, 
    and handle exceptions whereever needed. You will provide only the refactored code without any additional text before and after the code.

    If you receive anything but the code, you will answer that you can only do code refactoring and ask to provide the code.
    Code:
    {code}
    """
    
    # Assuming Ollama has a function `ollama.chat` to interact with the model
    # This will send the prompt to Ollama's LLM and get a response
    response = ollama.chat(model = selected_model, messages=[{
                                        'role': 'user',
                                        'content': prompt,
                                    },])
    
     # Extract the content from the response
    refactored_code = response['message']['content']
    
    # Clean up the output for better readability (e.g., removing extra spaces or newlines)
    refactored_code = refactored_code.strip()
    
    # Return the refactored code
    return refactored_code

# Function to handle code conversion based on user input
def convert_code(instruction, selected_model, raw_code):
    # Construct the prompt for code conversion (e.g., Next.js to React.js)
    prompt = f"""
    Instruction: {instruction}
    Code:
    {raw_code}
    """
    
    # Send the prompt to Ollama for conversion (adjust the model as needed)
    response = ollama.chat(
        model=selected_model,  # Model will be selected from dropdown 
        messages=[{
            'role': 'user',
            'content': prompt,
        }]
    )
    
    # Extract the content from the response (converted code)
    converted_code = response['message']['content']
    
    # Clean up the output for better readability (remove extra spaces or newlines)
    converted_code = converted_code.strip()
    
    return converted_code

def generate_pseudo_code(prompt):
    # Construct the prompt for generating pseudo code
    response = ollama.chat(
        model="qwen2.5-coder:14b",  # Adjust the model name as needed
        messages=[{
            'role': 'user',
            'content': f"You are an staff software engineer who design algorithm for complex taks in sofware industry, Generate pseudocode or algorithm for: {prompt}",
        }]
    )
    
    # Extract and clean up the pseudo code from the response
    pseudo_code = response['message']['content'].strip()
    
    return pseudo_code

def generate_final_code(pseudo_code):
    if not pseudo_code.strip():
        return "Error: No pseudo code provided. Please enter or generate pseudo code before converting."
    # Construct the prompt for generating the final code from the pseudo code
    response = ollama.chat(
        model="qwen2.5-coder:14b",  # Adjust the model name as needed
        messages=[{
            'role': 'user',
            'content': f"Please generate executable code from the following pseudo code:\n\n{pseudo_code}\n\nMake sure the code is in Python, complete and correct.",
        }]
    )
    
    # Extract and clean up the final code from the response
    final_code = response['message']['content'].strip()
    
    return final_code

# Set up the Gradio interface
with gr.Blocks() as demo:
    with gr.Tabs():
        # Tab 1 : Refactor and Comment Code
        with gr.Tab("Refactor and Comment Code"):
            # Fetch models dynamically
            model_choices = get_available_models()

            model_dropdown = gr.Dropdown(
                label="Select a Model", 
                choices=model_choices,
                value=model_choices[0],  # Default model
                type="value"
            )

            raw_code_input = gr.Textbox(label="Paste Your Raw Code")
            # Button for submitting the code
            submit_button = gr.Button("Submit")

            refactored_code_output = gr.Code(language="python", label="Refactored Code")

            submit_button.click(refactor_and_comment, inputs=[raw_code_input, model_dropdown], outputs=refactored_code_output)
        with gr.Tab("Convert Code"):
            # Dropdown for selecting model
            model_dropdown = gr.Dropdown(
                label="Select a Model", 
                choices=["codestral:latest", "qwen2.5-coder:32b", "qwen2.5-coder:14b"],  # Replace with actual available models
                value="codestral:latest",  # Default model
                type="value"
            )
            # Textbox for instruction (e.g., "Convert this Next.js code to React.js code")
            instruction_input = gr.Textbox(label="Instruction", placeholder="e.g., Convert this Next.js code to React.js code", lines=20)
            
            # Textbox for raw code (Next.js code, in this example)
            raw_code_input_convert = gr.Textbox(label="Raw Code (Next.js)", placeholder="Paste your Next.js code here")

            # Button for submitting the conversion task
            submit_button_convert = gr.Button("Convert")

            # Output the converted code (React.js code, in this example)
            converted_code_output = gr.Code(language="javascript", label="Converted Code (React.js)")

            # Link the submit button to the convert_code function
            submit_button_convert.click(convert_code, inputs=[instruction_input, model_dropdown,raw_code_input_convert], outputs=converted_code_output)

        with gr.Tab("Generate Code"):
        # Input for user's code generation request
            code_request_input = gr.Textbox(
                label="What code do you want to write?", 
                placeholder="e.g., Write a code for implementing quick sort", 
                lines=5
            )
            generate_pseudo_button = gr.Button("Generate Pseudo Code")
            pseudo_code_output = gr.Textbox(
                label="Pseudo Code", 
                placeholder="Generated pseudo code will appear here", 
                lines=10
            )
            generate_final_button = gr.Button("Generate Final Code")
            final_code_output = gr.Code(
                language="python",
                label="Final Code", 
                lines=10
            )

            # Linking the buttons to their functions
            generate_pseudo_button.click(
                generate_pseudo_code, 
                inputs=code_request_input, 
                outputs=pseudo_code_output
            )
            generate_final_button.click(
                generate_final_code, 
                inputs=pseudo_code_output, 
                outputs=final_code_output
            )

# Launch the Gradio app
demo.launch()

