import openai
from fastmcp import Client
import json
import os
import sys
import asyncio

#==========|| Variable Declarations ||======#
llm_client = openai.OpenAI(
    api_key="not-required",
    base_url="http://localhost:8080/v1"
)
mcp_client = Client(
    "http://localhost:8001/mcp"
)

#==========|| Utility Functions ||==========#
def convert_tool_obj(tool_obj):
    """Convert a tool object to a dictionary format."""
    tool_dict = {
        "name": tool_obj.name,
        "description": tool_obj.description
    }
    if hasattr(tool_obj, "inputSchema") and tool_obj.inputSchema:
        tool_dict["parameters"] = tool_obj.inputSchema
    else:
        tool_dict["parameters"] = {
            "type": "object",
            "properties": {}
        }
    return tool_dict

#==========|| Async Main Function ||========#
async def main():
    async with mcp_client:
        raw_tools = await mcp_client.list_tools()
        tools = []
        messages = []
        for tool_obj in raw_tools:
            tool_dict = convert_tool_obj(tool_obj)
            tools.append({"type": "function", "function": tool_dict})

        # print(raw_tools) # use for debugging
        # print(json.dumps(tools, indent=2)) # use for debugging
        print(f"Successfully retrieved {len(tools)} tools.")
        print("--- Streamlined LLM Chat Client ---")
        print("Type 'quit' or 'exit' to end the conversation.")
        print("-----------------------------------")

        while True:
            #----> 1) Get user input
            user_input = input("\nYou: ")
            if user_input.lower() in ["quit", "exit"]:
                print("Ending conversation. Goodbye!")
                break
            messages.append({"role": "user", "content": user_input})
            #----> 2) Get LLM response
            response = llm_client.chat.completions.create( # TO-DO: make async via AsyncOpenAI
                model="Wayland", # doesn't matter for llama.cpp
                messages=messages,
                tools=tools,
                tool_choice="auto",
                #stream=True
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                messages.append(response_message)

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f"--- LLM called tool: {function_name} with args {function_args} ---")

                    tool_result = await mcp_client.call_tool(
                        function_name,
                        function_args
                    )

                    print(f"--- MCP Server Response: {tool_result} ---")

                    tool_output_str = ""
                    if isinstance(tool_result, list) and len(tool_result) > 0:
                        if hasattr(tool_result[0], 'text'):
                            tool_output_str = str(tool_result[0].text)
                        else:
                            tool_output_str = str(tool_result[0])
                    else:
                        tool_output_str = str(tool_result)

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_output_str,
                    })

                second_response = llm_client.chat.completions.create(
                    model="Wayland",  # doesn't matter for llama.cpp
                    messages=messages,
                )
                final_response = second_response.choices[0].message.content
                print(f"Assistant: {final_response}")
                messages.append({
                    "role": "assistant",
                    "content": final_response,
                })

            else:
                final_response = response_message.content
                print(f"Assistant: {final_response}")
                messages.append({
                    "role": "assistant",
                    "content": final_response,
                })

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nConversation ended by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
                
        