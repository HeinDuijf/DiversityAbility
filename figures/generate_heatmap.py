import matplotlib.pyplot as plt
import seaborn as sns

from data_analysis.statistics import produce_df_1samp


def heatmap(
    outcome: str = "accuracy",
    diverse_team_type: str = "diverse",
    heuristic_size: int | list[int] = 5,
    n_sources_list: list[int] = [13, 17],
    measure: str = "absolute",
    colors: bool = False,
    show: bool = False,
    show_cbar: bool = True,
    filename: str | None = None,
):
    df = produce_df_1samp(
        outcome=outcome,
        diverse_team_type=diverse_team_type,
        heuristic_size=heuristic_size,
        n_sources_list=n_sources_list,
        compute_ci=False,
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
    plt.figure(figsize=(5, 3))

    heatmap_params = {
        # "annot": True,
        "cmap": "gray_r",  # "coolwarm"
        "square": True,
        "cbar": show_cbar,
        "cbar_kws": {"shrink": 0.4},
        "vmin": 0,
        "vmax": 10,
        "fmt": "",
    }
    df_heatmap = abs(pivot_df)
    annot_df = pivot_df.copy().map(lambda x: f"{x:.1f}")

    if colors:
        heatmap_params["cmap"] = "coolwarm"
        heatmap_params["center"] = 0
        df_heatmap = pivot_df

    if measure == "absolute":
        if colors:
            heatmap_params["vmin"] = -10
            heatmap_params["vmax"] = 10
        else:
            positives_df = pivot_df > 0.0
            annot_df[positives_df] = "+" + annot_df[positives_df]

    if measure == "relative":
        annot_df = pivot_df.copy().map(lambda x: f"{x:.0f}")
        heatmap_params["vmax"] = 100

        if colors:
            heatmap_params["vmin"] = -100
            heatmap_params["vmax"] = 100
        else:
            positives_df = pivot_df > 0.0
            annot_df[positives_df] = "+" + annot_df[positives_df]

    effect_df = df.pivot(index="rel_mean", columns="n_sources", values="effect_size")
    effect_low = effect_df < 0.1
    effect_mid = (effect_df >= 0.1) & (effect_df < 0.3)
    annot_df[effect_low] = annot_df[effect_low] + "'"
    annot_df[effect_mid] = annot_df[effect_mid] + "''"

    pvalue_df = df.pivot(
        index="rel_mean",
        columns="n_sources",
        values="p_value",
    )
    not_sig = pvalue_df > 0.001
    annot_df[not_sig] = ""

    heatmap_params["annot"] = annot_df

    fig = sns.heatmap(
        df_heatmap,
        **heatmap_params,
    )

    fig.set_xlabel("Sources (#)")
    fig.set_ylabel("Reliability (mean)")
    plt.yticks(rotation=0)

    if filename is None:
        filename = f"figures/images/heatmap_{outcome}_{measure}"
    plt.savefig(
        f"{filename}.eps",
        bbox_inches="tight",
        dpi=800,
        format="eps",
    )
    plt.savefig(
        f"{filename}.png",
        bbox_inches="tight",
        dpi=800,
    )
    if show:
        plt.show()
    plt.close()
