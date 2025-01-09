from data_analysis.heatmap import visualize_heatmap
from figures_scripts.hongpage import figure_hong_page
from figures_scripts.individual_scores import boxplot_individual_scores

if __name__ == "__main__":
    visualize_heatmap(outcome="accuracy")
    visualize_heatmap(outcome="pool_accuracy")
    visualize_heatmap(outcome="bounded_pool_accuracy")
    visualize_heatmap(outcome="accuracy", measure="relative")
    visualize_heatmap(outcome="pool_accuracy", measure="relative")
    visualize_heatmap(outcome="bounded_pool_accuracy", measure="relative")
    visualize_heatmap(outcome="average", measure="absolute")
    visualize_heatmap(outcome="average", measure="relative")
    boxplot_individual_scores()
    figure_hong_page()
