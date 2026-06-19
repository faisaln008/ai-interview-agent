from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    question: str
    answer: str

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def llm_node(state: AgentState) -> AgentState:
    response = llm.invoke(state["question"])
    return {"answer": response.content}

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("llm", llm_node)
    graph.set_entry_point("llm")
    graph.add_edge("llm", END)
    return graph.compile()

agent = build_graph()

async def run_agent(question: str) -> str:
    result = agent.invoke({"question": question, "answer": ""})
    return result["answer"]