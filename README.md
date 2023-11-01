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
between these three teams. 

[//]: # (This repository contains the code for the agent-based model and simulations, for )

[//]: # (producing some figures, and for the statistical analysis. To get a feel for the )

[//]: # (agent-based model, click the picture below:)

## 1. Setup
To run the project, you first need to install the required packages
```commandline
pip install -r requirements.txt
```

## 2. Simulation
1. To get a feel for the agent-based model, you can check out the
[jupyter notebook](NotebookWalkthrough.ipynb), which includes some network 
visualizations, by either opening the 
[pages](https://heinduijf.github.io/MajorityVotingCollectiveAccuracy/) or by running
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

3. To generate the figures, run the script
```commandline
python figures.py
```
which will create a folder `new_figures` containing all the figures. 

4. To run the statistical analysis, run the script
```commandline
python stats.py
```
which will create several csv files in the folder `stats_scripts` with the results of 
the statistical analysis.  

## 3. Organization of the project

### The agent-based model: `community.py`
The central class `Community` is defined in `community.py`. A `Community` is an 
*agent-based model* consisting of a network of agents, and it can be used to compute 
the estimated accuracy of a given community. The networks are generated with homophilic 
and preferential attachment. 

### Jupyter notebook: `NotebookWalkthrough.ipynb`
The jupyter notebook walks you through the stages of the agent-based model 
`Community` using some network visualizations. To minimalize the amount of code in the 
notebook, some scripts are stored in `scripts/notebook.py`, which is run in one of the 
initial notebook cells. 

### Simulations: `simulation.py`
The central class `Simulation` and method `Simulation.run()` is defined in 
`simulation.py`, the method produces the csv file `data/clean.csv`. The method 
`Simulation.run()` runs a simulation consisting of generating `number_of_communities` 
communities and estimating the accuracy of each community by running 
`number_of_voting_simulations` voting simulations.  

### Figures: `figures.py`
The script `figures.py` creates a folder `new_figures` containing all the 
figures. The folder `generate_figures` contains the scripts that generate 
figures. Each script in that folder is associated with one of the figures. 

### Statistical analysis: `stats.py`
The script `stats.py` runs the statistical analysis that generates several csv 
files in  the folder `stats_scripts`. The folder `stats_scripts` contains scripts that 
generate the csv files. Each script in that folder is associated with one of the csv 
files.

## 5. Licence and citation
This repository accompanies an academic paper (in progress). In the meantime, 
please cite as follows:
- TBD

Released under the [MIT licence](LICENCE.md).
