import anyio

from mcp import Client, StdioServerParameters
from mcp.types import TextContent, TextResourceContents


#  Configure the MCP 
server_params = StdioServerParameters(
    command=r"E:\mcp_learning\.venv\Scripts\python.exe",
    args=[r"E:\mcp_learning\server.py"]
)


async def main():

    # Connect to the MCP server
    async with Client(server_params) as client:

        print("\nConnected to MCP Server!")

        # Discover available tools
        tools = await client.list_tools()

        print("\nAvailable Tools:")

        for tool in tools.tools:
            print("-", tool.name)

        #  Call the addition tool
        print("\nCalling add tool...")

        result = await client.call_tool(
            "add",
            arguments={"a": 10, "b": 20}
        )

        print("\nAddition Result:")

        for content in result.content:
            if isinstance(content, TextContent):
                print(content.text)

        # Discover  resources
        resources = await client.list_resources()

        print("\nAvailable Resources:")

        for resource in resources.resources:
            print(resource.uri)

        # Read a static resource
        print("\nReading project overview...")

        resource_result = await client.read_resource(
            "project://overview"
        )

        for content in resource_result.contents:
            if isinstance(content, TextResourceContents):
                print(content.text)

        #  Discover  prompts
        prompts = await client.list_prompts()

        print("\nAvailable Prompts:")

        for prompt in prompts.prompts:
            print("-", prompt.name)

        # Retrieve a prompt
        if any(p.name == "explain_python_code" for p in prompts.prompts):

            prompt_result = await client.get_prompt(
                "explain_python_code",
                arguments={
                    "code": "def square(n): return n * n"
                }
            )

            print("\nRetrieved Prompt:")

            for message in prompt_result.messages:
                print(message.role)
                print(message.content)


if __name__ == "__main__":
    anyio.run(main)
