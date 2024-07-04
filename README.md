# Diversity and Ability

This repository is associated with a working paper on the 
diversity-ability-randomness trade-off in collective problem-solving. The background 
is [Hong and Page's (2004)](https://doi.org/10.1073/pnas.0403723101) infamous 
diversity trumps ability (DTA) theorem: 

> We find that when selecting a problem-solving 
team from a diverse population of intelligent agents, a team of randomly selected 
agents outperforms a team comprised of the best-performing agents.

This repository 
investigates the collective problem-solving capacities of teams in a new formal 
framework: a probabilistic source-reliability model. We consider three types of 
teams:
1. Teams consisting of the best-performing agents;
2. Teams consisting of a (cognitively) diverse set of agents;
3. Teams consisting of a randomly selected agents. 

Preliminary (!) findings suggest that there is no significant performance difference 
between these three types of teams. To get a feel for the 
agent-based model, see the picture below and the [Jupyter Notebook](/NotebookWalkthrough.ipynb).

[![A picture of an example of a team consisting of randomly selected agents](/www/example_random_team.png "An example of an agent-based model")]()


## 1. Setup
To run the project, you first need to install the required packages
```commandline
pip install -r requirements.txt
```

## 2. Simulation
1. To get a feel for the agent-based model, you can check out this
[Jupyter Notebook](NotebookWalkthrough.ipynb), which includes some network 
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
which will create a csv file `data/clean.csv`, a collection of communities in the 
folder `data/communities`, and a README file with the parameter settings for the 
simulation in `data/README.csv`.

3. To see the preliminary data analysis, check out this [Jupyter Notebook](DataAnalysis.ipynb) by running
```commandline
jupyter-notebook DataAnalysis.ipynb
```
 

## 3. Organization of the project

### Illustration of the agent-based model: `NotebookWalkthrough.ipynb`
The Jupyter Notebook walks you through the stages of the agent-based model 
`Community` using some network visualizations. To minimalize the amount of code in the 
notebook, some scripts are stored in `utils/notebook.py`, which is run in one of the 
initial notebook cells. 

### The agent-based model: `community.py`
The central class `Community` is defined in `community.py`. A `Community` is an 
*agent-based model* consisting of a network of sources and agents. The central method `estimated_community_accuracy` computes the estimated accuracy of the group of agents. 

### Determine the three types of teams: `determine_teams.py`
The central methods for determining the three types of teams can be found in `determine_teams.py`: `best_team`, `diverse_team`, and `random_team`.

### Data analysis (preliminary): `DataAnalysis.ipynb`
The Jupyter Notebook contains a preliminary analysis of results. The notebook contains some statistical analyses and some graphs illustrating the trade-off between ability, diversity and randomness. 

### Simulations: `simulation.py`
The central class `Simulation` and method `Simulation.run()` is defined in 
`simulation.py`, the method produces the csv files in the folder `data`. The 
method `Simulation.run()` runs a simulation consisting of generating 
`number_of_communities` communities and creating the three types of teams for each 
community and estimating the accuracy of each team by running 
`number_of_voting_simulations` voting simulations.

## 5. Computational limitations
* This repository is not optimized for computational speed, but for findability, accessibility, interoperability, and reusability ([FAIR](https://www.uu.nl/en/research/research-data-management/guides/how-to-make-your-data-fair)).
* Determining the team consisting of random agents and best-performing agents is fast, but determining the team of diverse agents is slow (see `determine_teams.py`). The computational cost of computing the most diverse team goes up if the number of sources increases. Hence, the reason why I have only considered at most 21 sources. 

## 6. Licence and citation
This repository accompanies an academic paper (in progress). In the meantime, please cite as follows:
- TBD

Released under the [MIT licence](LICENCE.md).
