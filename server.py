from mcp.server import MCPServer
from pathlib import Path


# Create an MCP server
mcp = MCPServer("Calculator Server")

# addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers and  result."""
    return a + b


# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract the second number from the first number."""
    return a - b


# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers and result."""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide the first number by the second number."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@mcp.tool()
def celsius_to_fahrenheit(celsius: float) -> float:
    """temperature from Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32

@mcp.tool()
def fahrenheit_to_celsius(fahrenheit: float)->float:
    """temperature from Fahrenheit to Celsius ."""
    return (fahrenheit-32)*(5/9)
@mcp.tool()
def calculate_birth_year(age: int, current_year: int) -> int:
    """Estimate birth year using age and current year."""

    if age < 0:
        raise ValueError("Age cannot be negative")

    if age > 120:
        raise ValueError("Age must be 120 or below")

    if current_year < 1900:
        raise ValueError("Invalid current year")

    return current_year - age

@mcp.tool()
def read_project_file(filename: str) -> str:
    """Read a permitted text file from the MCP project directory."""

    # Project directory
    base_dir = Path(__file__).resolve().parent

    # Resolve the requested file
    file_path = (base_dir / filename).resolve()
    if not file_path.is_relative_to(base_dir):
        raise ValueError("Access outside the project directory is not allowed")

    if file_path.suffix.lower() not in [".txt", ".md", ".py"]:
        raise ValueError("Unsupported file type")
    if not file_path.is_file():
        raise FileNotFoundError("File not found")
    if file_path.stat().st_size > 100_000:
        raise ValueError("File is too large")
    return file_path.read_text(encoding="utf-8")

#resource 

# Static resource
@mcp.resource(
    "project://overview",
    name="project_overview",
    description="General information about the MCP learning project."
)
def get_project_overview() -> str:
    """Provide an overview of the MCP learning project."""

    return """
    Project: MCP Learning
    Language: Python
    Framework: MCP Python SDK
    Purpose: Learn MCP development.
    """


#  Resource template
@mcp.resource(
    "project://files/{filename}",
    name="project_file",
    description="Read an allowed text file from the project directory."
)
def get_project_file(filename: str) -> str:
    """Read a permitted text file from the project directory."""

    base_dir = Path(__file__).resolve().parent

    if filename != Path(filename).name or filename in {".", ".."}:
        raise ValueError("Only filenames in the project directory are allowed")

    file_path = (base_dir / filename).resolve()
    if not file_path.is_relative_to(base_dir):
        raise ValueError("Access outside project directory is not allowed")
    if file_path.suffix.lower() not in [".txt", ".md"]:
        raise ValueError("Only TXT and MD files are allowed")
    if not file_path.is_file():
        raise FileNotFoundError("File not found")
    if file_path.stat().st_size > 100_000:
        raise ValueError("File is too large")

    return file_path.read_text(encoding="utf-8")

@mcp.prompt()
def explain_python_code(code: str) -> str:
    """Explain Python code in simple, step-by-step terms."""

    return f"""
    Explain the following Python code.

    Include:
    1. Purpose of the code.
    2. Explanation of each important line.
    3. Python concepts used.
    4. Expected output.
    5. A simple real-world example.

    Code:
    {code}
    """
@mcp.prompt()
def review_python_code(
    code: str,
    language: str = "python"
) -> str:
    """Review code and identify bugs, security issues and improvements."""

    return f"""
    Act as an experienced {language} developer.

    Review the following code.

    Identify:
    1. Syntax errors.
    2. Logical errors.
    3. Performance issues.
    4. Security problems.
    5. Code quality improvements.

    Provide corrected code where necessary.

    Code:
    {code}
    """
@mcp.prompt()
def analyze_ml_results(
    algorithm: str,
    accuracy: str,
    precision: str,
    recall: str,
    f1_score: str
) -> str:
    """Analyze machine learning evaluation metrics."""

    return f"""
    Act as a machine learning expert.

    Analyze the following model evaluation results.

    Algorithm: {algorithm}
    Accuracy: {accuracy}
    Precision: {precision}
    Recall: {recall}
    F1 Score: {f1_score}

    Explain:

    1. What these metrics indicate.
    2. Whether the model performs well.
    3. Possible weaknesses.
    4. Whether the model may be overfitting.
    5. Suggestions for improvement.

    Provide a clear conclusion.
    """
if __name__ == "__main__":
    mcp.run()
