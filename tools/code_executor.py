import subprocess
import tempfile
from langchain_core.tools import tool

@tool
def execute_python_code(code: str) -> str:
    """
    Executes Python code in a temporary subprocess and returns the standard output and error.
    Use this tool whenever you need to run Python scripts, test logic, perform math, or build an application (e.g. a Snake game).
    Be sure to include any needed imports within the code.
    """
    try:
        # Create a temporary file to hold the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file_path = f.name
        
        # Execute the python script
        result = subprocess.run(
            ['python3', temp_file_path],
            capture_output=True,
            text=True,
            timeout=30 # Prevent infinite loops
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
            
        return output if output.strip() else "Code executed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Execution timed out after 30 seconds."
    except Exception as e:
        return f"An error occurred during execution: {str(e)}"
