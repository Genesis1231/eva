from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from core.classes import EvaState
from core.nodes import (
    eva_initialize, 
    eva_end, 
    eva_conversate, 
    eva_sense, 
    eva_action,
    router_sense, 
    router_action, 
    router_action_results,
)

load_dotenv()

def launch_eva():
    workflow = StateGraph(EvaState)

    workflow.add_node("node_initialize", eva_initialize)
    workflow.add_node("node_sense", eva_sense)
    workflow.add_node("node_conversate", eva_conversate)
    workflow.add_node("node_action", eva_action)
    workflow.add_node("node_end", eva_end)


    workflow.set_entry_point("node_initialize")
    workflow.add_edge("node_initialize", "node_conversate")
    workflow.add_conditional_edges("node_conversate", router_action)
    workflow.add_conditional_edges("node_action", router_action_results)
    workflow.add_conditional_edges("node_sense", router_sense)

    workflow.add_edge("node_end", END)

    eva = workflow.compile()
    eva.invoke({"status": "initialize"}, {"recursion_limit": 100000})

if __name__ == "__main__":
    launch_eva()

