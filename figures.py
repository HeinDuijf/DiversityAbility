from figures_scripts.heatmap import visualize_heatmap
from figures_scripts.hongpage import figure_hong_page
from figures_scripts.individual_scores import boxplot_individual_scores

if __name__ == "__main__":
    colors = False
    visualize_heatmap(outcome="accuracy", colors=colors)
    visualize_heatmap(outcome="pool_accuracy", colors=colors)
    visualize_heatmap(outcome="bounded_pool_accuracy", colors=colors)
    visualize_heatmap(outcome="accuracy", measure="relative", colors=colors)
    visualize_heatmap(outcome="pool_accuracy", measure="relative", colors=colors)
    visualize_heatmap(
        outcome="bounded_pool_accuracy", measure="relative", colors=colors
    )
    visualize_heatmap(outcome="average", measure="absolute", colors=colors)
    visualize_heatmap(outcome="average", measure="relative", colors=colors)
    boxplot_individual_scores()
    figure_hong_page()
