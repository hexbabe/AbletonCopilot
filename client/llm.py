from openai import OpenAI
import os
import ast
from dotenv import load_dotenv
import re
from client.client import LiveClient
from protocol.protocol import *
import json


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=api_key)

# Initialize the LiveClient here
live_client = LiveClient()

def parse_python_file(filepath):
    """Parses a Python file and extracts function information and dataclass definitions."""
    with open(filepath, "r") as file:
        source = file.read()

    tree = ast.parse(source)
    functions = []
    dataclasses = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Exclude dunder methods and the run_tests function
            if not node.name.startswith("__") and node.name != "run_tests":
                function_info = {
                    "name": node.name,
                    "parameters": [
                        {
                            "name": arg.arg,
                            "type": ast.unparse(arg.annotation) if arg.annotation else None
                        } for arg in node.args.args if arg.arg != 'self'
                    ],
                    "return_type": ast.unparse(node.returns) if node.returns else None,
                    "docstring": ast.get_docstring(node) or ""
                }
                functions.append(function_info)
        
        # Look for dataclass definitions
        elif isinstance(node, ast.ClassDef):
            # Check if class has dataclass decorator
            if any(isinstance(d, ast.Name) and d.id == 'dataclass' 
                  or (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == 'dataclass')
                  for d in node.decorator_list):
                fields = []
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        # Get field type annotation as string
                        type_annotation = ast.unparse(item.annotation)
                        fields.append({
                            "name": item.target.id,
                            "type": type_annotation,
                            "default": ast.unparse(item.value) if item.value else None
                        })
                
                dataclass_info = {
                    "name": node.name,
                    "fields": fields,
                    "docstring": ast.get_docstring(node) or ""
                }
                dataclasses.append(dataclass_info)

    return {
        "functions": functions,
        "dataclasses": dataclasses
    }

def format_api_info_text(api_info, protocol_info):
    """Formats API information and protocol definitions as a plain text list for the LLM."""
    formatted_text = "Available API Methods:\n"
    
    # Add function information
    for method in api_info["functions"]:
        params = [f"{param} (optional)" for param in method['parameters']]
        formatted_text += f"  * {method['name']}({', '.join(params)}):\n"
        if method['docstring']:
            formatted_text += f"    {method['docstring']}\n"
    
    # Add dataclass information
    formatted_text += "\nData Structures:\n"
    for dataclass in protocol_info["dataclasses"]:
        formatted_text += f"  * {dataclass['name']}:\n"
        if dataclass['docstring']:
            formatted_text += f"    {dataclass['docstring']}\n"
        for field in dataclass['fields']:
            default_str = f" = {field['default']}" if field['default'] else ""
            formatted_text += f"    - {field['name']}: {field['type']}{default_str}\n"
    
    return formatted_text

def call_llm_with_api(user_prompt, api_filepaths):
    """
    Calls the OpenAI LLM, providing it with API information and the user's prompt.

    Args:
        user_prompt: The user's request.
        api_filepaths: List of paths to Python files containing API methods and protocols.
    """

    # Parse both files
    api_methods = parse_python_file(api_filepaths[0])  # client.py
    protocol_info = parse_python_file(api_filepaths[1])  # protocol.py
    
    api_info = format_api_info_text(api_methods, protocol_info)

    system_prompt = f"""
You are a helpful music production and mixing engineer assistant to the user. You are also well-versed in musical theory and composition
and every genre of music. You are also creative. Finding ways to use the available API and Ableton to fulfill users' potentially
abstract prompts.

You can control the DAW remotely using a Python client to fulfill any of the user's requests.
In this version of the app, the DAW is Ableton Live. Follow Ableton Live's terminology, conventions, and UX,
when executing the user's requests.

If the user's prompt indicates an action that can be done in the DAW by you via Python, follow the below instructions for executing the action.
If the user's prompt does not indicate an action for you to take on the DAW, do not execute code. Remember that the prompt
can be somewhat abstract and may not match 1:1 with what you know about the methods. You have to be creative sometimes
and infer what needs to be done e.g. if a user says "add a guitar riff midi to a new track" you should infer that they want
to create a midi track and clip with notes that belong in a guitar riff.

Remember you don't need to be super constrained to using only the context provided in the code and in the API methods.
Don't be afraid to use your general knowledge to aid the user in fulfilling their goal.

All method arguments are optional. When you want to omit an argument, simply don't include it in the arguments object.

Here are the available API methods you can use:

{api_info}

Respond with a JSON string containing a list of API calls to be executed in order. Each API call should have:
- "function_name": The name of the function to call
- "arguments": An object with parameter names as keys and their values. Only include parameters you want to set.

Example format:
[{{"function_name": "create_midi_track", "arguments": {{"name": "Piano"}}}}]

Do not include any comments in the JSON and code you output.

Do not provide any other explanation or text. Do not confirm. Do not ask further questions.
If the user's request cannot be fulfilled creatively by using/chaining available API method calls,
respond with "ERROR: Cannot fulfill request with available API methods." Along with a short description
of why you can't fulfill the request.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return completion.choices[0].message.content

def remove_json_comments(json_string):
    """Removes C-style comments from a JSON string."""
    # Remove // comments
    json_string = re.sub(r"//.*?\n", "\n", json_string)
    # Remove /* comments */
    json_string = re.sub(r"/\*.*?\*/", "", json_string, flags=re.DOTALL)
    return json_string

def execute_api_calls(response, api_methods):
    """
    Parses the LLM response, validates each API call, and executes them in sequence.
    """
    try:
        # Handle potential markdown code block formatting and remove comments.
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:-3].strip()
        response = remove_json_comments(response)

        api_calls = json.loads(response)

        if not isinstance(api_calls, list):
            raise ValueError("Invalid response format: Expected a list of API calls.")

    except json.JSONDecodeError:
        print("ERROR: Invalid response format. Could not parse JSON.")
        return
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    for call in api_calls:
        function_name = call.get("function_name")
        arguments_dict = call.get("arguments", {})

        # Validate function name
        valid_function_names = [method["name"] for method in api_methods]
        if function_name not in valid_function_names:
            print(f"ERROR: Unknown function '{function_name}'")
            continue

        # Get the method's expected parameters
        method_info = next(m for m in api_methods if m["name"] == function_name)
        expected_params = [param["name"] for param in method_info["parameters"]]

        # Create a list of arguments, using None for any missing parameters
        arguments = [arguments_dict.get(param) for param in expected_params]

        try:
            api_method = getattr(live_client, function_name)
            print(f"Executing: {function_name}({', '.join(map(str, arguments))})")
            
            response = api_method(*arguments)

            if response.success:
                print(f"Successfully executed API call. Response: {response.data}")
            else:
                print(f"API call failed. Error: {response.error}")

        except Exception as e:
            print(f"ERROR: Could not execute API call: {e}")

if __name__ == "__main__":
    api_filepath = "./client/client.py"
    protocol_filepath = "./protocol/protocol.py"
    # "create a midi track and clip containing the C major scale. don't forget to make the clip first before adding notes."
    user_prompt = input("Enter a prompt: ")

    response = call_llm_with_api(user_prompt, [api_filepath, protocol_filepath])
    print(f"LLM Response: {response}")

    # Execute the API calls if the response is not an error
    if not response.startswith("ERROR"):
        api_methods = parse_python_file(api_filepath)["functions"]  # Only need functions for execution
        execute_api_calls(response, api_methods)
