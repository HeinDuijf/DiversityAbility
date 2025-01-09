import copy
import glob
import os
import random as rd

import config as cfg
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import pyvis
import seaborn as sns
from pyvis.network import Network

from models.agent import Agent
from models.generate_teams import (
    generate_diverse_team,
    generate_expert_team,
    generate_random_team,
)
from models.sources import Sources
from models.team import Team

correct_color = "forestgreen"
incorrect_color = "firebrick"
agent_initial_color = "darkorange"
source_initial_color = "teal"


def visualize(
    team: Team,
    sorting: str = "degree",
    sizing: str = "reliability",
    coloring: str = "initial",
    edge_type: str = "vertical",
    filename: str = None,
    show: bool = True,
) -> Network:
    net = Network(
        height="200px",
        width="100%",
        directed=True,
        notebook=True,
        neighborhood_highlight=True,
        cdn_resources="in_line",
        layout=True,
    )

    sources_ordered = sort_sources(team, sorting)
    sources_coloring = color_sources(team, coloring)
    sources_sizing = size_sources(team, sizing)
    agents_coloring = color_agents(team, coloring)

    for source in sources_ordered:
        net.add_node(
            f"s{source}",
            title=f"Reliability {team.sources.reliabilities[source]}",
            label=True,
            color=sources_coloring[source],
            level=1,
            size=sources_sizing[source],
        )

    for agent_no, agent in enumerate(team.members):
        net.add_node(
            agent_no,
            title=f"Agent {agent_no}",
            color=agents_coloring[agent],
            level=4,
            size=20,
        )
    net.set_edge_smooth(edge_type)
    for agent_no, agent in enumerate(team.members):
        for source in agent.heuristic:
            net.add_edge(
                source=agent_no, to=f"s{source}", color=sources_coloring[source]
            )

    net.hrepulsion(node_distance=200, damping=0.1)
    net.prep_notebook()
    return net


def sort_sources(team: Team, sorting: str = "degree") -> list:
    sources_tuples = [(0, 0)]
    heuristics = np.array([agent.heuristic for agent in team.members]).flatten()
    unique, counts = np.unique(heuristics, return_counts=True)
    source_degrees_dict = dict(zip(unique, counts))
    for source in team.sources.sources:
        if source not in source_degrees_dict.keys():
            source_degrees_dict[source] = 0

    if sorting == "degree":
        sources_tuples = [
            (
                source,
                source_degrees_dict[source],
                team.sources.reliabilities[source],
            )
            for source in team.sources.sources
        ]
    elif sorting == "reliability":
        sources_tuples = [
            (
                source,
                team.sources.reliabilities[source],
                source_degrees_dict[source],
            )
            for source in team.sources.sources
        ]
    sources_tuples.sort(key=lambda item: item[2], reverse=True)
    sources_tuples.sort(key=lambda item: item[1], reverse=True)
    sources_ordered, _, _ = zip(*sources_tuples)
    return sources_ordered


def color_sources(team: Team, coloring: str) -> dict:
    sources_coloring = {source: source_initial_color for source in team.sources.sources}

    for source in team.sources.sources:
        if coloring == "sources" or coloring == "agents":
            if team.sources.valences[source] == cfg.vote_for_positive:
                sources_coloring[source] = correct_color
            else:
                sources_coloring[source] = incorrect_color
    return sources_coloring


def size_sources(team: Team, sizing: str) -> dict:
    source_sizing = {source: 1 for source in team.sources.sources}
    heuristics = np.array([agent.heuristic for agent in team.members]).flatten()
    unique, counts = np.unique(heuristics, return_counts=True)
    source_degrees_dict = dict(zip(unique, counts))
    if sizing == "degree":
        source_sizing = {source: source_degrees_dict for source in team.sources.sources}
    elif sizing == "reliability":
        source_sizing = {
            source: team.sources.reliabilities[source]
            for source in team.sources.sources
        }
    minimum = min(source_sizing.values())
    maximum = max(source_sizing.values())
    for source in team.sources.sources:
        source_sizing[source] = 10 + 40 * (source_sizing[source] - minimum) / (
            maximum - minimum
        )
    return source_sizing


def color_agents(team: Team, coloring: str) -> dict:
    agents_coloring = {agent: agent_initial_color for agent in team.members}
    for agent in team.members:
        if coloring == "agents":
            if agent.opinion == cfg.vote_for_positive:
                agents_coloring[agent] = correct_color
            else:
                agents_coloring[agent] = incorrect_color
    return agents_coloring
