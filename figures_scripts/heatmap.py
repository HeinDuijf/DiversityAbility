import matplotlib.pyplot as plt
import seaborn as sns

from data_analysis.statistics import produce_df_1samp


def visualize_heatmap(
    outcome: str = "accuracy",
    measure: str = "absolute",
    mask: bool = True,
    colors: bool = False,
    show: bool = False,
):
    df = produce_df_1samp(outcome)
    if measure == "absolute":
        df["effect_percent"] = 100 * df["difference"]
    if measure == "relative":
        df["effect_percent"] = df["error_reduction"]
    pivot_df = df.pivot(
        index="rel_mean",
        columns="n_sources",
        values="effect_percent",
    )
    pivot_df.sort_index(inplace=True, ascending=False)

    sns.set_style("white")
    font_style = {"family": "Times New Roman", "size": 12}
    plt.rc("font", **font_style)
    plt.figure(figsize=(2, 3))

    heatmap_params = {
        # "annot": True,
        "cmap": "gray_r",  # "coolwarm"
        "square": True,
        "cbar_kws": {"shrink": 0.4},
    }
    if colors:
        heatmap_params["cmap"] = "coolwarm"
        heatmap_params["center"] = 0

    if measure == "absolute":
        heatmap_params["vmin"] = -10
        heatmap_params["vmax"] = 10
        heatmap_params["annot"] = True
        if not colors:
            labels = pivot_df.copy()
            labels = labels.astype(str).map(
                lambda x: (
                    ("+" + x).split(".")[0] + "." + ("+" + x).split(".")[1][0]
                    if "-" not in x
                    else x.split(".")[0] + "." + x.split(".")[1][0]
                )
                # lambda x: ("+" + x)[:4] if "-" not in x else x[:4]
            )
            heatmap_params["annot"] = labels
            heatmap_params["fmt"] = ""
            heatmap_params["vmin"] = 0

    if measure == "relative":
        heatmap_params["vmin"] = -100
        heatmap_params["vmax"] = 100
        heatmap_params["fmt"] = "g"
        heatmap_params["annot"] = True
        if not colors:
            labels = pivot_df.copy()
            labels = labels.astype(str).map(
                lambda x: ("+" + x).split(".")[0] if "-" not in x else x.split(".")[0]
            )
            heatmap_params["annot"] = labels
            heatmap_params["fmt"] = ""
            heatmap_params["vmin"] = 0

    if not mask:
        fig = sns.heatmap(abs(pivot_df), **heatmap_params)
    else:
        mask_df = df.pivot(
            index="rel_mean",
            columns="n_sources",
            values="p_value",
        )
        mask_df = mask_df.astype(bool)
        mask_df.sort_index(inplace=True, ascending=False)
        fig = sns.heatmap(
            abs(pivot_df),
            mask=mask_df,
            # annot=labels,
            **heatmap_params,
        )

    fig.set_xlabel("Sources (#)")
    fig.set_ylabel("Reliability (mean)")
    plt.yticks(rotation=0)
    # fig.set_title(f"Expert vs diverse teams:\n{outcome} (in %)\n")
    plt.savefig(
        f"figures/heatmap_{outcome}_{measure}.eps",
        bbox_inches="tight",
        dpi=800,
        format="eps",
    )
    plt.savefig(
        f"figures/heatmap_{outcome}_{measure}.png",
        bbox_inches="tight",
        dpi=800,
    )
    if show:
        plt.show()
    plt.close()
