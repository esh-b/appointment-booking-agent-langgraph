from typing_extensions import TypedDict
from typing import Annotated
import datetime
import pytz

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

from agent.tools import convert_relative_to_absolute_datetime, check_availability, book_appointment
from agent.prompts import AGENT_SYSTEM_MESSAGE_PROMPT


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


available_tools = [convert_relative_to_absolute_datetime, check_availability, book_appointment]
tool_node = ToolNode(tools=available_tools)
_llm_with_tools = ChatOpenAI(model='gpt-4o').bind_tools(tools=available_tools)
system_message = {
    'role': 'developer', 
    'content': AGENT_SYSTEM_MESSAGE_PROMPT.format(
        current_dt_iso=datetime.datetime.now(tz=pytz.timezone('America/Toronto')))
}


def llm_call(state: AgentState):
    response = _llm_with_tools.invoke([system_message] + state['messages'])
    return {'messages': [response]}


def get_graph_builder_object():
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("llm_call", llm_call)
    graph_builder.add_node("tool_node", tool_node)
    graph_builder.add_edge(START, 'llm_call')
    graph_builder.add_conditional_edges(
        'llm_call', 
        tools_condition, 
        {'tools': 'tool_node', END: END}
    )
    graph_builder.add_edge('tool_node', 'llm_call')
    return graph_builder


_memory_saver = MemorySaver()
_graph_builder = get_graph_builder_object()
booking_agent_graph = _graph_builder.compile(checkpointer=_memory_saver)
