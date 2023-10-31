import os
import random as rd

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import seaborn as sns
from community import Community
from pyvis.network import Network

from config import vote_for_negative, vote_for_positive

elite_color = "#FFC107"
mass_color = "#9C27B0"


def set_node_attributes(com: Community, color_type: str = "type"):
    def translate_to_color(symbol):
        if symbol == vote_for_negative or symbol == "elite":
            return elite_color
        else:
            return mass_color

    for node in com.agents:
        com.influence_network.agents[node]["label"] = str(node)
        com.influence_network.agents[node]["size"] = (
            com.influence_network.in_degree(node) + 1
        )
        com.influence_network.agents[node]["level"] = com.influence_network.in_degree(
            node
        )
        if color_type == "type":
            com.influence_network.agents[node]["color"] = translate_to_color(
                com.influence_network.agents[node]["type"]
            )
        elif color_type == "opinion":
            com.influence_network.agents[node]["color"] = translate_to_color(
                com.influence_network.agents[node]["opinion"]
            )
        elif color_type == "vote":
            com.influence_network.agents[node]["color"] = translate_to_color(
                com.influence_network.agents[node]["vote"]
            )


def visualize(com: Community, color_type="type"):
    set_node_attributes(com=com, color_type=color_type)
    nt = Network(
        height="500px",
        width="100%",
        directed=True,
        notebook=True,
        neighborhood_highlight=True,
        cdn_resources="remote",
    )
    nt.set_edge_smooth("curvedCCW")
    for node in com.agents_elite:
        nt.add_node(node, x=-1000, **com.influence_network.agents[node])
    for node in com.agents_mass:
        nt.add_node(node, x=1000, **com.influence_network.agents[node])

    hide_edges = False
    if color_type == "vote":
        hide_edges = True
    elif color_type == "type":
        nt.inherit_edge_colors(False)

    for edge in com.influence_network.edges():
        nt.add_edge(
            edge[0],
            edge[1],
            hidden=hide_edges,
            color=com.influence_network.agents[edge[1]]["color"],
        )
    nt.hrepulsion(node_distance=200, damping=0.4)
    nt.prep_notebook()
    return nt
