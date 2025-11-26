import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def figure_hong_page():
    font_style = {"family": "Times New Roman", "size": 12}
    plt.rc("font", **font_style)
    plt.figure(figsize=(5, 4))

    locations = np.arange(1, 13, dtype=int)
    values = [
        25,
        32,
        88,
        12,
        33,
        14,
        20,
        87,
        75,
        84,
        68,
        40,
    ]  # rd.sample(sorted(possible_values), 12)
    edges = [(1, 2), (2, 5), (5, 10), (10, 3)]

    net = nx.DiGraph()
    net.add_nodes_from(locations)
    net.add_edges_from(edges)

    pos_dummy = nx.circular_layout(net)
    pos = {location: pos_dummy[((3 - location) % 12 + 1)] for location in locations}
    labels = {location: f"{location}: {values[location - 1]}" for location in locations}

    nx.draw_networkx_nodes(net, pos=pos, node_color="w", node_size=1500, edgecolors="k")
    nx.draw_networkx_labels(net, pos=pos, font_size=11, labels=labels)

    nx.draw_networkx_edges(
        net,
        pos=pos,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=20,
        node_size=1500,
        connectionstyle="arc3,rad=0.3",
    )
    # nx.draw_networkx_edge_labels(
    #     net, pos, edge_labels=edge_labels, connectionstyle="arc3,rad=0.3"
    # )

    plt.axis("off")
    axis = plt.gca()
    axis.set_xlim([1.2 * x for x in axis.get_xlim()])  # type: ignore
    axis.set_ylim([1.2 * y for y in axis.get_ylim()])  # type: ignore
    plt.tight_layout()
    plt.savefig("figures/images/hongpage.eps", dpi=800, format="eps")
    plt.savefig("figures/images/hongpage.png", dpi=800)
    plt.close()
    # plt.show()
