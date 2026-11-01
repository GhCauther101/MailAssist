from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode
from tools import *
from utils import *
from llm import *
from langgraph.graph import MessagesState, StateGraph, START, END

llm = llm.bind_tools([list_unread_emails, summarize_email])

tools = [
    list_unread_emails,
    summarize_email
]

# Make tools available to the LLM
llm_with_tools = llm.bind_tools(tools)

# Tool execution node
tool_node = ToolNode(tools)

SYSTEM_PROMPT = """
You are MailAssist, an intelligent email assistant.

Your task is to help users retrieve and summarize their emails.

RULES:

1. Before summarizing an email, call list_unread_emails.

2. Read the actual JSON response returned by the tool.

3. Never invent, guess, or generate email UIDs.

4. Only use UIDs that actually appear in the list_unread_emails
   response.

5. If there are no unread emails, inform the user.

6. If there is exactly one unread email, retrieve and summarize it.

7. If there are multiple unread emails, ask the user which email
   they want summarized.

8. When the user identifies an email by subject or sender,
   match it against the returned email list.

9. Call summarize_email with the actual numeric UID.

10. After retrieving the email body, summarize it concisely.

11. Never call summarize_email with placeholder text.

12. Do not claim to have retrieved or summarized an email
    unless the corresponding tool returned its content.
"""


def llm_node(state: MessagesState):

    print("\n[LLM Node] Processing conversation.")

    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + state["messages"]

    response = llm_with_tools.invoke(messages)

    print("[LLM Node] Response generated.")

    return {
        "messages": [response]
    }


def router(state: MessagesState):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        print("[Router] Routing to tools.")
        return "tools"

    print("[Router] Routing to END.")

    return "end"


builder = StateGraph(MessagesState)
builder.add_node("llm", llm_node)
builder.add_node("tools", tool_node)
builder.add_edge(START, "llm")
builder.add_edge("tools", "llm")
builder.add_conditional_edges(
    "llm",
    router,
    {
        "tools": "tools",
        "end": END
    }
)
graph = builder.compile()