# mypy: disable-error-code="union-attr"
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

LOCATION = "us-central1"
LLM = "gemini-2.0-flash-001"

# 1. Define tools (connectors)
@tool
def kinaxis_connector(query: str) -> str:
    """Simulates interacting with Kinaxis"""
    return f"Kinaxis data for: {query}"

# @tool
# def sap_connector(query: str) -> str:
#     """Simulates interacting with SAP"""
#     return f"SAP data for: {query}"

# @tool
# def salesforce_connector(query: str) -> str:
#     """Simulates interacting with Salesforce"""
#     return f"Salesforce data for: {query}"

# tools = [kinaxis_connector, sap_connector, salesforce_connector]

# invoice_tools = [sap_connector]
# due_diligence_tools = [kinaxis_connector]
# finance_tools = [salesforce_connector]

# procesing_tools = [invoice_tools, due_diligence_tools, finance_tools]
procesing_tools = [kinaxis_connector]


# 2. Set up the language model
llm = ChatVertexAI(
    model=LLM, location=LOCATION, temperature=0, max_tokens=1024, streaming=True
).bind_tools(procesing_tools) 

# 3. Define workflow components
def invoice_agent(state: MessagesState, config: RunnableConfig) -> dict[str, BaseMessage]:
    """Simulates the invoice agent."""
    system_message = "You are the invoice agent. Extract invoice data and decide where to send it."
    messages_with_system = [{"type": "system", "content": system_message}] + state["messages"]
    response = llm.invoke(messages_with_system, config)
    return {"messages": response}

# def due_diligence_agent(state: MessagesState, config: RunnableConfig) -> dict[str, BaseMessage]:
#     """Simulates the due diligence agent."""
#     system_message = "You are the due diligence agent. Check contracts and OTIF."
#     messages_with_system = [{"type": "system", "content": system_message}] + state["messages"]
#     response = llm.invoke(messages_with_system, config)
#     return {"messages": response}

def finance_agent(state: MessagesState, config: RunnableConfig) -> dict[str, BaseMessage]:
    """Simulates the finance agent."""
    system_message = "You are the finance agent. Identify optimization opportunities."
    messages_with_system = [{"type": "system", "content": system_message}] + state["messages"]
    response = llm.invoke(messages_with_system, config)
    return {"messages": response}

def should_continue(state: MessagesState) -> str:
    """Determines whether to use tools or end the conversation."""
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else "due_diligence_agent"

# def should_continue_finance(state: MessagesState) -> str:
#     """Determines whether to use tools or end the conversation."""
#     last_message = state["messages"][-1]
#     return "tools" if last_message.tool_calls else END

# def should_continue_due_diligence(state: MessagesState) -> str:
#     """Determines whether to use tools or end the conversation."""
#     last_message = state["messages"][-1]
#     return "tools" if last_message.tool_calls else END

# 4. Create the workflow graph
workflow = StateGraph(MessagesState)
workflow.add_node("invoice_agent", invoice_agent)
# workflow.add_node("due_diligence_agent", due_diligence_agent)
workflow.add_node("finance_agent", finance_agent)
workflow.add_node("tools", ToolNode(procesing_tools)) 

workflow.set_entry_point("invoice_agent")

# 5. Define graph edges
workflow.add_conditional_edges("invoice_agent", should_continue)
workflow.add_conditional_edges("finance_agent", should_continue)
# workflow.add_conditional_edges("due_diligence_agent", should_continue_due_diligence)

workflow.add_edge("tools", "invoice_agent")
# workflow.add_edge("invoice_agent","due_diligence_agent")
# workflow.add_edge("due_diligence_agent","finance_agent")
workflow.add_edge("finance_agent","invoice_agent")

# 6. Compile the workflow
agent = workflow.compile()
