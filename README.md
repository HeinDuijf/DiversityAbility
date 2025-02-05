# Diversity and Ability

This repository is associated with a working paper on the 
diversity-expertise trade-off in collective problem-solving. The background 
is [Hong and Page's (2004)](https://doi.org/10.1073/pnas.0403723101) infamous 
diversity trumps ability (DTA) results: 

> We find that when selecting a problem-solving 
team from a diverse population of intelligent agents, a team of randomly selected 
agents outperforms a team comprised of the best-performing agents.

This repository 
investigates the collective problem-solving capacities of teams in a new formal 
framework: a (probabilistic) source reliability model. We consider three types of 
teams:
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
jupyter-notebook NotebookWalkthrough.ipynb
```
Running the notebook will create several html files in the folder `www` with 
visualizations of agent-based models.

2. To run the simulations and generate the data, run the script
```commandline
python main.py
```
which will create several csv files in the folder `data`.

3. To check out the data analysis, you can run this [Jupyter Notebook](DataAnalysis.ipynb) by running
```commandline
jupyter-notebook DataAnalysis.ipynb
```

## 3. Organization of the project

### Illustration of the agent-based model: `NotebookWalkthrough.ipynb`
The Jupyter Notebook walks you through the stages of the agent-based model `Team` using some network visualizations. To minimalize the amount of code in the notebook, some scripts are stored in `utils/notebook.py`, which is run in one of the initial notebook cells. 

### The agent-based model: `models/team.py`
The central class `Team` is defined in `models/team.py`. A `Team` is an *agent-based model* consisting of sources and agents. The central method `accuracy` computes the accuracy of the team. 

### Determine the three types of teams: `models/generate_teams.py`
The central methods for determining the three types of teams can be found in `models/generate_teams.py`: `generate_expert_team`, `generate_diverse_team`, and `generate_random_team`.

### Data analysis: `DataAnalysis.ipynb`
The Jupyter Notebook contains an analysis of results. The notebook contains some statistical analyses and some graphs illustrating the trade-off between expertise and diversity. Some of the scripts used for the data analysis can be found in the folder `data_analysis`.

### Simulations: `simulation.py` and `grid_simulation.py`
The class `Simulation` and method `Simulation.run()` is defined in `simulation.py`, the method produces a csv file (typically, in the folder `data`). The method `Simulation.run()` runs a simulation for a particular parameter setting and produces results that can give insight into whether diversity trumps ability for that parameter setting. 

The class `GridSimulation` and method `GridSimulation.run()` is defined in `grid_simulation.py`. The method runs simulations (by invoking the method `Simulation.run()`) for each parameter setting in a grid. 

### Figures: `figures.py`
The figures in the paper can be reproduced by running `figures.py`. This will create the figures in the folder `figure` by calling scripts in `figures_scripts` and `data_analysis/heatmap`.

## 5. Computational limitations
* This repository is not optimized for computational speed, but for findability, accessibility, interoperability, and reusability ([FAIR](https://www.uu.nl/en/research/research-data-management/guides/how-to-make-your-data-fair)).
* Determining the accuracy of teams can be computationally demanding. The computational cost of computing the accuracy of a team goes up if the number of sources increases. Although this was still somewhat feasible for 17 sources (approx. 2 hours per parameter setting), it is no longer feasible for 21 sources.  

## 6. Licence and citation
This repository accompanies an academic paper (in progress). In the meantime, please cite as follows:
- Duijf, H. (2025). Diversity and ability in a source reliability model. _GitHub_. https://github.com/HeinDuijf/DiversityAbility 

Released under the [MIT licence](LICENCE.md).
