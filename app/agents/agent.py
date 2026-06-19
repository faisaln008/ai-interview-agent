from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langsmith import traceable
from typing import TypedDict

class AgentState(TypedDict):
    question: str
    answer: str
    messages: list

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def llm_node(state: AgentState) -> AgentState:
    # Build the full message list from prior history plus the current question.
    messages = list(state.get("messages", []))
    messages.append(HumanMessage(content=state["question"]))
    response = llm.invoke(messages)
    return {"answer": response.content}

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("llm", llm_node)
    graph.set_entry_point("llm")
    graph.add_edge("llm", END)
    return graph.compile()

agent = build_graph()

@traceable(name="run-agent")
async def run_agent(question: str, history: list = []) -> str:
    # Convert stored history rows into LangChain message objects.
    messages = []
    for entry in history:
        messages.append(HumanMessage(content=entry["question"]))
        messages.append(AIMessage(content=entry["answer"]))

    result = agent.invoke({"question": question, "answer": "", "messages": messages})
    return result["answer"]
