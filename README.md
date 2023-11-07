# Diversity and Ability

This repository is associated with a working paper on the 
diversity-ability-randomness trade-off in collective problem-solving. The background 
is [Hong and Page's (2004)](https://doi.org/10.1073/pnas.0403723101) infamous 
diversity trumps ability (DTA) theorem: "We find that when selecting a problem-solving 
team from a diverse population of intelligent agents, a team of randomly selected 
agents outperforms a team comprised of the best-performing agents."  This repository 
investigates the collective problem-solving capacities of teams in a new formal 
framework: a probabilistic source-reliability model. We consider three types of 
teams:
1. Teams consisting of the best-performing agents;
2. Teams consisting of a (cognitively) diverse set of agents;
3. Teams consisting of a randomly selected agents. 

Preliminary findings suggest that there is no significant performance difference 
between these three types of teams. To get a feel for the 
agent-based model, see the picture below and the [Jupyter Notebook](/NotebookWalkthrough.ipynb).

[![A picture of an example of a team consisting of randomly selected agents](/www/example_random_team.png "An example of an agent-based model")]()


## 1. Setup
To run the project, you first need to install the required packages
```commandline
pip install -r requirements.txt
```

## 2. Simulation
1. To get a feel for the agent-based model, you can check out the
[jupyter notebook](NotebookWalkthrough.ipynb), which includes some network 
visualizations, by running
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

3. To see the preliminary data analysis, run the jupyter notebook
```commandline
jupyter-notebook DataAnalysis.ipynb
```
which will open a jupyter notebook in your browser.  

## 3. Organization of the project

### Jupyter notebook: `NotebookWalkthrough.ipynb`
The jupyter notebook walks you through the stages of the agent-based model 
`Community` using some network visualizations. To minimalize the amount of code in the 
notebook, some scripts are stored in `scripts/notebook.py`, which is run in one of the 
initial notebook cells. 

### The agent-based model: `community.py`
The central class `Community` is defined in `community.py`. A `Community` is an 
*agent-based model* consisting of a network of sources and agents, and it can be 
used to compute the estimated accuracy of a given group of agents. 

### Jupyter notebook: `DataAnalysis.ipynb`
The jupyter notebook contains a preliminary analysis of the agent-based model based 
on some simulations. The notebook contains some graphs that illustrate the trade-off 
between ability, diversity and randomness. 

### Simulations: `simulation.py`
The central class `Simulation` and method `Simulation.run()` is defined in 
`simulation.py`, the method produces the csv files in the folder `data`. The 
method `Simulation.run()` runs a simulation consisting of generating 
`number_of_communities` communities and creating the three types of teams for each 
community and estimating the accuracy of each team by running 
`number_of_voting_simulations` voting simulations.

## 5. Licence and citation
This repository accompanies an academic paper (in progress). In the meantime, 
please cite as follows:
- TBD

Released under the [MIT licence](LICENCE.md).
