import os
import ctypes
import datetime
import struct
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from the .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define constants
EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002
EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004
EVERYTHING_REQUEST_EXTENSION = 0x00000008
EVERYTHING_REQUEST_SIZE = 0x00000010
EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040

# Load Everything DLL
everything_dll = ctypes.WinDLL(r"C:\Users\Mtweve Familly\Downloads\Everything-SDK\dll\Everything64.dll")
everything_dll.Everything_SetRequestFlags(EVERYTHING_REQUEST_FILE_NAME | EVERYTHING_REQUEST_PATH | EVERYTHING_REQUEST_SIZE | EVERYTHING_REQUEST_DATE_MODIFIED)

# Function to perform file search using Everything
def search_files(filename):
    """Search for files using Everything."""
    # Setup search with the provided file name
    everything_dll.Everything_SetSearchW(filename)
    # Execute the query
    everything_dll.Everything_QueryW(1)
    # Get the number of results
    num_results = everything_dll.Everything_GetNumResults()
    
    # Create a list to store file paths
    file_paths = []
    
    # Iterate over results and retrieve file paths
    for i in range(num_results):
        # Create buffer to store file path
        file_path = ctypes.create_unicode_buffer(260)
        # Get file path for the current result
        everything_dll.Everything_GetResultFullPathNameW(i, file_path, 260)
        # Append file path to the list
        file_paths.append(file_path.value)
    
    return file_paths
# Function to parse file name from OpenAI response
def parse_file_name(openai_response):
    """Parse file name from OpenAI response."""
    # Extract the file name from the OpenAI response
    file_name = json.loads(openai_response.function_call.arguments).get("file_name")
    return file_name

# Example usage
user_prompt = "look for happy files related "



function_descriptions = [
    {
        "name": "find_file",
        "description": "Get files information from my computer",
        "parameters": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "The file's name, e.g  test.py or key words like dragon ball",
                },
                
            },
            "required": ["file_name"],
        },
    }
]



# Get OpenAI response
completion = client.chat.completions.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "user", "content": user_prompt}],
    # Add function calling
    functions=function_descriptions,
    function_call="auto",  # specify the function call
)

print(completion)
# Parse file name from OpenAI response
file_name = parse_file_name(completion.choices[0].message)


if file_name:
    # Perform file search using Everything
    file_paths = search_files(file_name)
    
    # Display the search results
    print(f"Search Results for '{file_name}':")
    for path in file_paths:
        print(path)
    print(f"Total {len(file_paths)} files found.")
else:
    print("File name not found in the OpenAI response.")
