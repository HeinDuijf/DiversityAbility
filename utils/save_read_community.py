import os
import pickle

from community import Community


def community_compress(community: Community):
    edges_dict = {}
    for source, target in community.influence_network.edges():
        if source not in edges_dict.keys():
            edges_dict[source] = f"{target}"
        else:
            edges_dict[source] = f"{edges_dict[source]},{target}"
    source_edges_dict = {}
    for agent, source in community.source_network.edges():
        if agent not in source_edges_dict.keys():
            source_edges_dict[f"S{agent}"] = f"{source}"
        else:
            source_edges_dict[f"S{agent}"] = f"{source_edges_dict[agent]},{source}"
    community_dict = {
        "N": community.number_of_agents,
        # "E": community.number_of_elites,
        "d": community.influence_degree,
        "NS": community.number_of_sources,
        "ds": community.source_degree,
        **edges_dict,
        **source_edges_dict,
    }
    return community_dict


def community_unpack(community_compressed: dict):
    agents = [
        agent
        for agent in range(community_compressed["N"])
        if agent in community_compressed.keys()
    ]
    edges = [
        (source, int(target))
        for source in agents
        for target in agents
        if str(target) in community_compressed[source].split(",")
    ]
    sources = [
        source for source in [f"s{k}" for k in range(community_compressed["NS"])]
    ]
    source_edges = [
        (agent, source)
        for agent in agents
        for source in sources
        if str(source) in community_compressed[f"S{agent}"].split(",")
    ]
    community_dict = {
        "number_of_agents": community_compressed["N"],
        "influence_degree": community_compressed["d"],
        "number_of_sources": community_compressed["NS"],
        "source_degree": community_compressed["ds"],
        "edges": edges,
        "source_edges": source_edges,
    }
    community = Community(**community_dict)
    return community


def save_community_to_file(filename: str, community: Community):
    path = os.path.dirname(filename).replace("\\", "/")
    os.makedirs(path, exist_ok=True)
    community_compressed = community_compress(community)
    with open(f"{filename}.pickle", "wb") as f:
        pickle.dump(community_compressed, f)


def read_community_from_file(filename: str):
    with open(f"{filename}.pickle", "rb") as f:
        community_compressed = pickle.load(f)
    community = community_unpack(community_compressed)
    return community
