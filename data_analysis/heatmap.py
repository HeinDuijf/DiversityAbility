import matplotlib.pyplot as plt
import seaborn as sns

from data_analysis.statistics import produce_df_1samp


def visualize_heatmap(
    outcome: str = "accuracy",
    measure: str = "absolute",
    mask: bool = True,
):
    df = produce_df_1samp(outcome)
    if measure == "absolute":
        df["effect_percent"] = 100 * df["difference"]
    if measure == "relative":
        df["effect_percent"] = df["error_reduction"].astype("int64")
    pivot_df = df.pivot(
        index="rel_mean",
        columns="n_sources",
        values="effect_percent",
    )
    pivot_df.sort_index(inplace=True, ascending=False)

    sns.set_style("white")
    font_style = {"family": "Calibri", "size": 16}
    plt.rc("font", **font_style)
    plt.figure(figsize=(2, 4))

    heatmap_params = {
        "annot": True,
        "cmap": "coolwarm",  # "gray_r",
        "square": True,
        "cbar_kws": {"shrink": 0.4},
        "center": 0,
    }
    if measure == "absolute":
        heatmap_params["vmin"] = -10
        heatmap_params["vmax"] = 10

    if measure == "relative":
        heatmap_params["vmin"] = -100
        heatmap_params["vmax"] = 100
        heatmap_params["fmt"] = "g"

    if not mask:
        fig = sns.heatmap(pivot_df, **heatmap_params)
    else:
        mask_df = df.pivot(
            index="rel_mean",
            columns="n_sources",
            values="p_value",
        )
        mask_df = mask_df.astype(bool)
        mask_df.sort_index(inplace=True, ascending=False)
        fig = sns.heatmap(
            pivot_df,
            mask=mask_df,
            **heatmap_params,
        )

    fig.set_xlabel("Sources (#)")
    fig.set_ylabel("Reliability (mean)")
    plt.yticks(rotation=0)
    # fig.set_title(f"Expert vs diverse teams:\n{outcome} (in %)\n")
    plt.savefig(f"figures/heatmap_{outcome}_{measure}", bbox_inches="tight")
    return fig
