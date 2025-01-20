from dataclasses import dataclass
from typing import Callable, TypedDict
import json

from openai.types.chat import ChatCompletionMessageToolCall


class ToolParam(TypedDict):
    type: str
    description: str


@dataclass
class Tool:
    """
    A tool is a function that can be called by the GPT Agent.
    """
    fun: Callable
    description: str
    params: dict[str, ToolParam] | None


available_tools: dict[str, Tool] = {}


def tool(description: str, params: dict[str, ToolParam] | None = None):
    """
    Decorator to register a function as a tool.
    @param description: A description of the tool.
    @param params: A dictionary of parameters to the tool
    """
    def wrapper(fun: Callable):
        new_tool: Tool = Tool(fun, description, params)
        available_tools[fun.__name__] = new_tool
        return fun

    return wrapper


class ToolManager:
    """
    A class to manage the available tools.
    """
    @staticmethod
    def list_available_tools():
        """
        List the available tools in a format that can be used by OpenAI API.
        """
        tools = []
        toolname: str
        for toolname in available_tools:
            tool = available_tools[toolname]
            json_tool = {
                "type": "function",
                "function": {
                    "name": tool.fun.__name__,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.params if tool.params is not None else {},
                    },
                    "required": [name for name in tool.params]
                    if tool.params is not None
                    else [],
                },
            }
            tools.append(json_tool)
        return tools

    @staticmethod
    def get_toolkit(tool_call: ChatCompletionMessageToolCall):
        """
        Get the function and arguments for a tool call.
        """
        tool = available_tools[tool_call.function.name]
        print(tool_call.function)
        args = json.loads(tool_call.function.arguments)

        return (tool.fun, args)
