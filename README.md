# Diversity and Ability

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17899031.svg)](https://doi.org/10.5281/zenodo.17899031)   

This repository is associated with the paper ‘Diversity and expertise in binary classification problems’, which is accepted at [_Philosophy of Science_](https://www.cambridge.org/core/journals/philosophy-of-science) ([PhilSci Archive](https://philsci-archive.pitt.edu/id/eprint/26428)). Here's the abstract: 

> Democratic theorists and social epistemologists often celebrate the epistemic benefits of diversity. One of the cornerstones is the ‘diversity trumps ability’ result by [Hong and Page (2004)](https://doi.org/10.1073/pnas.0403723101). Ironically, the interplay between diversity and ability is rarely studied in radically different frameworks. Although diversity has been studied in prediction and search problems, the diversity-expertise trade-off has not been studied systematically for small, deliberative groups facing binary classification problems. To fill this gap, I will introduce a new evidential sources framework and study whether, when, and (if so) why diversity trumps expertise in binary classification problems. The newly gained insights are used to revisit the epistemic credentials of deliberative democracy.

This repository investigates the collective problem-solving capacities of teams in a new evidential sources framework. The simulation study focuses on expert and diverse teams, but the repository also coverse random teams:
1. Expert teams consisting of the best-performing agents;
2. Diverse teams consisting of a (cognitively) diverse set of agents;
3. Random teams consisting of a randomly selected agents. 

To get a feel for the 
agent-based model, see the picture below and the [Jupyter Notebook](/NotebookWalkthrough.ipynb) or the [GitHub page](https://heinduijf.github.io/DiversityAbility/).

[![A picture of an example of a team consisting of randomly selected agents](/www/example_random_team.png "An example of an agent-based model")]()


## 1. Setup
To run the project, you first need to install the required packages
```commandline
pip install -r requirements.txt
```

## 2. Simulation
1. To get a feel for the agent-based model, you can check out this
[Jupyter Notebook](NotebookWalkthrough.ipynb) (or the [GitHub page](https://heinduijf.github.io/DiversityAbility/)), which includes some network 
visualizations by running
```commandline
jupyter lab NotebookWalkthrough.ipynb
```
Running the cells in the notebook will create several html files in the folder `www` with 
visualizations of agent-based models.

2. To run the simulations and generate the data, run the script
```commandline
python main.py
```
which will create several csv files in the folder `data`.

3. To check out the data analysis, you can run this [Jupyter Notebook](DataAnalysis.ipynb) by running
```commandline
jupyter lab DataAnalysis.ipynb
```

## 3. Organization of the repository

### Illustration of the agent-based model: notebook `NotebookWalkthrough.ipynb` and folder `www` (also see the [GitHub page](https://heinduijf.github.io/DiversityAbility/))
The Jupyter Notebook walks through the stages of the agent-based model `Team` using some network visualizations. Running the notebook will create visualizations in the folder `www`. These can also be viewed on the [GitHub page](https://heinduijf.github.io/DiversityAbility/). 

### Models: folder `models`

- The agent-based model is implemented in the central class `Team`, which is located in `models/team.py`. A `Team` is an *agent-based model* consisting of sources and agents. The central methods `accuracy_opinion`, `accuracy_evidence` and `accuracy_bounded` compute the accuracy of the team for the opinion-based, evidence-based and boundedly rational evidence-based dynamics, respectively.

- The class `Team` relies on the classes `Sources` and `Agent` implementing the sources (and their reliability) ant the agents (and their heuristics), which are located `models/sources.py` and `models/agent.py`, respectively. 

- The central methods for generating the three types of teams can be found in `models/generate_teams.py`: `generate_expert_team`, `generate_diverse_team`, and `generate_random_team`.

### Data analysis: folder `data_analysis` and notebook `DataAnalysis.ipynb`
The notebook contains statistical results and heatmaps illustrating the trade-off between expertise and diversity. It relies on the scripts for the Wilcoxon test, which are located in `data_analysis/statistics.py`. The scripts to compare expert teams to the best-performing individual are located in `data_analysis/expert_team_vs_individual.py`.

### Simulations: `simulation.py` and `grid_simulation.py`
The class `Simulation` and method `Simulation.run()` is located in `simulation.py`, the method produces a csv file (by default, in the folder `data`). The method `Simulation.run()` runs a simulation for a particular parameter setting and produces results that can give insight into whether diversity trumps ability for that parameter setting. 

The class `GridSimulation` and method `GridSimulation.run()` is located in `grid_simulation.py`. The method runs simulations (by invoking the method `Simulation.run()`) for each parameter setting in a grid. 

### Figures: `figures.py`
The figures in the paper can be reproduced by running `figures.py`, but it requires the necessary simulation data in `data`. This will create the figures in the folder `figures/images` by running scripts in the folder `figures`, especially the `heatmap` script located in `figures/generate_heatmap.py`.

### Robustness analysis: `Robustness.ipynb`
The notebook contains various robustness checks for the main simulation results. 

### Hong and Page's model: `models/landscape_model.py`
The class `Landscape` is an implementation of the landscape model (by [Alice Huang](https://github.com/alicecwhuang/noisy-search/tree/master)). Running the script will produce a csv file `data/landscape.csv`, which contains simulation results supporting my claim that landscape models cannot address sparse decision problems.

### Analytical approaches: `Analytical.ipynb`
The notebook considers the question of whether the diversity-expertise tradeoff (as modelled by the evidential sources model) can be studied analytically, using approaches from the voting literature. To investigate this, it covers: (1) A lower bound in terms of number of sources and their mean reliability; (2) The Cantelli lower bound (in terms of $\mu$ and $\sigma$); and (3) Normal approximation. 

## 5. Computational limitations
* This repository is not optimized for computational speed, but for findability, accessibility, interoperability, and reusability ([FAIR](https://www.uu.nl/en/research/research-data-management/guides/how-to-make-your-data-fair)).
* Determining the accuracy of teams can be computationally demanding. The computational cost of computing the accuracy of a team goes up if the number of sources increases. Although this was still somewhat feasible for 17 sources (approx. 2 hours per parameter setting), it is no longer feasible for 21 sources.  

## 6. Licence and citation
This repository accompanies an academic paper. Please cite this repository as follows:
- Duijf, H. (2025). _Diversity and ability in an evidential sources framework_. Zenodo. https://doi.org/10.5281/zenodo.17899031

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17899031.svg)](https://doi.org/10.5281/zenodo.17899031)
 

Released under the [MIT licence](LICENCE.md).
