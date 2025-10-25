import matplotlib.pyplot as plt
import seaborn as sns

from data_analysis.statistics import produce_df_1samp


def visualize_heatmap(
    outcome: str = "accuracy",
    diverse_team_type: str = "diverse",
    heuristic_size: int = 5,
    measure: str = "absolute",
    mask: bool = True,
    colors: bool = False,
    show: bool = False,
):
    df = produce_df_1samp(
        outcome=outcome,
        diverse_team_type=diverse_team_type,
        heuristic_size=heuristic_size,
        perform_bca_ci=False,
    )
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
    df_heatmap = abs(pivot_df)
    if colors:
        heatmap_params["cmap"] = "coolwarm"
        heatmap_params["center"] = 0
        df_heatmap = pivot_df

    if measure == "absolute":
        heatmap_params["vmin"] = -10
        heatmap_params["vmax"] = 10
        heatmap_params["annot"] = True
        if not colors:
            labels = pivot_df.copy()
            labels = labels.map(
                lambda x: (f"+{x:.1f}" if "-" not in str(x) else f"{x:.1f}")
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
            labels = labels.map(
                lambda x: f"+{x:.0f}" if "-" not in str(x) else f"{x:.0f}"
            )
            heatmap_params["annot"] = labels
            heatmap_params["fmt"] = ""
            heatmap_params["vmin"] = 0

    if not mask:
        fig = sns.heatmap(df_heatmap, **heatmap_params)
    else:
        mask_df = df.pivot(
            index="rel_mean",
            columns="n_sources",
            values="p_value",
        )
        mask_df = mask_df.astype(bool)
        mask_df.sort_index(inplace=True, ascending=False)
        fig = sns.heatmap(
            df_heatmap,
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
