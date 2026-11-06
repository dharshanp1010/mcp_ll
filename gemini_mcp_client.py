
import os
import anyio

from google import genai
from google.genai import types

from mcp import Client, StdioServerParameters
from mcp.types import TextContent


MODEL_NAME = "gemini-3.5-flash-lite"


# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not configured."
    )

gemini = genai.Client(api_key=api_key)


# Configure the MCP server process
server_params = StdioServerParameters(
    command=r"E:\mcp_learning\.venv\Scripts\python.exe",
    args=[r"E:\mcp_learning\server.py"]
)


def convert_mcp_tools_to_gemini(mcp_tools):
    """
    Convert MCP tool definitions into Gemini function declarations.
    """

    declarations = []

    for tool in mcp_tools.tools:

        declaration = types.FunctionDeclaration(
            name=tool.name,
            description=tool.description or tool.name,
            parameters_json_schema=tool.input_schema
        )

        declarations.append(declaration)

    return types.Tool(
        function_declarations=declarations
    )


def get_tool_result(result):
    """
    Convert an MCP result into a JSON-compatible value
    that can be sent back to Gemini.
    """

    if result.is_error:
        messages = []

        for block in result.content:
            if isinstance(block, TextContent):
                messages.append(block.text)

        return {"error": "\n".join(messages)}

    if result.structured_content is not None:
        return result.structured_content

    messages = []

    for block in result.content:
        if isinstance(block, TextContent):
            messages.append(block.text)

    return {"result": "\n".join(messages)}


async def main():

    # Connect to the MCP server
    async with Client(server_params) as mcp_client:

        print("Connected to MCP server!")

        # Discover available MCP tools
        mcp_tools = await mcp_client.list_tools()

        print("\nAvailable MCP tools:")

        for tool in mcp_tools.tools:
            print("-", tool.name)

        # Convert MCP tools into Gemini declarations
        gemini_tools = convert_mcp_tools_to_gemini(mcp_tools)

        # Create a Gemini chat with the discovered tools
        chat = gemini.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                tools=[gemini_tools]
            )
        )

        print("\nGemini MCP Assistant is ready!")
        print("Type 'exit' to stop.")

        while True:

            user_input = input("\nYou: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("Assistant stopped.")
                break

            if not user_input:
                continue

            # Send the user's request to Gemini
            response = chat.send_message(user_input)

            # Handle tool calls, including multiple rounds
            while response.function_calls:

                function_response_parts = []

                for function_call in response.function_calls:

                    tool_name = function_call.name
                    tool_arguments = function_call.args or {}

                    print(f"\nGemini selected MCP tool: {tool_name}")
                    print("Arguments:", tool_arguments)

                    # Execute the selected MCP tool
                    tool_result = await mcp_client.call_tool(
                        tool_name,
                        arguments=tool_arguments
                    )

                    result_for_gemini = get_tool_result(tool_result)

                    # Build a function response for Gemini
                    function_response = types.FunctionResponse(
                        id=function_call.id,
                        name=tool_name,
                        response=result_for_gemini
                    )

                    function_response_parts.append(
                        types.Part(function_response=function_response)
                    )

                # Send MCP results back to Gemini
                response = chat.send_message(
                    function_response_parts
                )

            # Display Gemini's final answer
            print("\nAssistant:", response.text or "(No text response)")


if __name__ == "__main__":
    anyio.run(main)
