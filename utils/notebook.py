import glob
import os
import random as rd

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import pyvis
import seaborn as sns
from community import Community
from pyvis.network import Network

import config as cfg

correct_color = "forestgreen"
incorrect_color = "firebrick"
agent_initial_color = "darkorange"
source_initial_color = "teal"


def visualize(
    com: Community,
    sorting: str = "degree",
    sizing: str = "reliability",
    coloring: str = "initial",
    edge_type="vertical",
):
    net = Network(
        height="500px",
        width="100%",
        directed=True,
        notebook=True,
        neighborhood_highlight=True,
        cdn_resources="remote",
        layout=True,
    )

    sources_ordered = sort_sources(com, sorting)
    sources_coloring = color_sources(com, coloring)
    sources_sizing = size_sources(com, sizing)
    agents_coloring = color_agents(com, coloring)

    for source in sources_ordered:
        net.add_node(
            source,
            title=f"Reliability {com.source_network.nodes[source][cfg.source_reliability]}",
            label=True,
            color=sources_coloring[source],
            level=1,
            size=sources_sizing[source],
        )

    for agent in com.agents:
        net.add_node(
            agent,
            title=f"Agent {agent}",
            color=agents_coloring[agent],
            level=4,
            size=10,
        )
    net.set_edge_smooth(edge_type)
    for edge in com.source_network.edges:
        net.add_edge(source=edge[0], to=edge[1], color=sources_coloring[edge[1]])
    net.hrepulsion(node_distance=200, damping=0.4)
    net.prep_notebook()
    return net


def sort_sources(com: Community, sorting: str = "degree"):
    sources_tuples = [(0, 0)]
    if sorting == "degree":
        sources_tuples = [
            (source, com.source_network.in_degree[source]) for source in com.sources
        ]
    elif sorting == "reliability":
        sources_tuples = [
            (source, com.source_network.nodes[source][cfg.source_reliability])
            for source in com.sources
        ]
    sources_tuples.sort(key=lambda item: item[1], reverse=True)
    sources_ordered, _ = zip(*sources_tuples)
    return sources_ordered


def color_sources(com: Community, coloring):
    sources_coloring = {source: source_initial_color for source in com.sources}

    for source in com.sources:
        if coloring == "sources" or coloring == "agents":
            if (
                com.source_network.nodes[source][cfg.source_valence]
                == cfg.vote_for_positive
            ):
                sources_coloring[source] = correct_color
            else:
                sources_coloring[source] = incorrect_color
    return sources_coloring


def size_sources(com: Community, sizing):
    source_sizing = {source: 1 for source in com.sources}
    if sizing == "degree":
        source_sizing = {
            source: com.source_network.in_degree[source] for source in com.sources
        }
    elif sizing == "reliability":
        source_sizing = {
            source: com.source_network.nodes[source][cfg.source_reliability]
            for source in com.sources
        }
    minimum = min(source_sizing.values())
    maximum = max(source_sizing.values())
    for source in com.sources:
        source_sizing[source] = (
            50 * (source_sizing[source] - minimum) / (maximum - minimum)
        )
    return source_sizing


def color_agents(com: Community, coloring):
    agents_coloring = {agent: agent_initial_color for agent in com.agents}
    for agent in com.agents:
        if coloring == "agents":
            if (
                com.influence_network.nodes[agent][cfg.agent_opinion]
                == cfg.vote_for_positive
            ):
                agents_coloring[agent] = correct_color
            else:
                agents_coloring[agent] = incorrect_color
    return agents_coloring
