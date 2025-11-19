from figures_scripts.generate_heatmap import heatmap
from figures_scripts.hongpage import figure_hong_page
from figures_scripts.individual_scores import boxplot_individual_scores

if __name__ == "__main__":
    colors = False
    heatmap(outcome="accuracy_opinion", colors=colors)
    heatmap(outcome="accuracy_evidence", colors=colors)
    heatmap(outcome="accuracy_bounded", colors=colors)
    heatmap(outcome="accuracy_opinion", measure="relative", colors=colors)
    heatmap(outcome="accuracy_evidence", measure="relative", colors=colors)
    heatmap(outcome="accuracy_bounded", measure="relative", colors=colors)
    heatmap(outcome="average", measure="absolute", colors=colors)
    heatmap(outcome="average", measure="relative", colors=colors)
    boxplot_individual_scores()
    figure_hong_page()
