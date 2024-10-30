from langgraph.graph import StateGraph, END, START
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

class EVA:
    """
    Class to construct the assistant.
    nodes:
        - initialize: Initialize the assistant.
        - sense: Let EVA sense the environment.
        - conversate: Main execution node.
        - action: Use tools to perform actions.
        - end: End the session.
    """
    
    def __init__(self) -> None:
        self.workflow = self._initialize_graph()
        self.app = self.workflow.compile()
        self.app.invoke({"status": "initialize"}, {"recursion_limit": 100000})


    def _initialize_graph(self)-> StateGraph:
        workflow = StateGraph(EvaState)
        workflow.add_node("node_initialize", eva_initialize)
        workflow.add_node("node_sense", eva_sense)
        workflow.add_node("node_conversate", eva_conversate)
        workflow.add_node("node_action", eva_action)
        workflow.add_node("node_end", eva_end)


        workflow.add_edge(START, "node_initialize")
        workflow.add_edge("node_initialize", "node_conversate")
        workflow.add_conditional_edges("node_conversate", router_action)
        workflow.add_conditional_edges("node_action", router_action_results)
        workflow.add_conditional_edges("node_sense", router_sense)

        workflow.add_edge("node_end", END)
        
        return workflow

