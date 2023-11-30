from dataclasses import dataclass
from typing import Callable, TypedDict
import json

from openai.types.chat import ChatCompletionMessageToolCall

class ToolParam(TypedDict):
    type: str
    description: str

@dataclass
class Tool:
    fun: Callable
    description: str
    params: dict[str,ToolParam]

    

available_tools: dict[str,Tool] = {}


def tool(description: str, params: dict[str,ToolParam]):
    def wrapper(fun: Callable):
        new_tool: Tool = Tool(fun, description, params)
        available_tools[fun.__name__] = new_tool
        return fun
    return wrapper

class ToolManager:
    @staticmethod
    def list_available_tools():
        tools = []
        toolname: str
        for toolname in available_tools:
            tool = available_tools[toolname]
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.fun.__name__,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.params
                    },
                    "required": [name for name in tool.params]
                },
            })
        return tools

    @staticmethod
    def get_toolkit(tool_call: ChatCompletionMessageToolCall):
        tool = available_tools[tool_call.function.name]
        print(tool_call.function)
        args = json.loads(tool_call.function.arguments)

        return (tool.fun, args)
