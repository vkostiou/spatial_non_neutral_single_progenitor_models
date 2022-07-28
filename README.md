# Introduction

This repository contains the spatial single progenitor models that simulate the collective behaviour of cells in epithelial tissues and the spread of mutant cells. It also contains a collection of python scripts for analysing the outputs of model simulations.

# Directory Structure:

 - **downstream**: contains the downstream feedback model
 - **upstream**: contains the upstream feedback model
 - **unified**: contains the model that enables both downstream and upstream feedback for mutant competition simulations
 - **analysis**: contains python scripts for analysing the simulation outputs. 

 Each model directory contains the following files:

- `densityFeedback.nlogo`: NetLogo model
- `config.nls`: Configuration file for changing parameters to modify model behaviour
- `SP_essentials.nls`: essential helper functions
- `report.nls`: helper functions for generating and saving output files
- **netlogo_output**: Directories for storing output files - initially empty. For enabling see generate_views, generate_ world parameters in `config.nls`
- **analysis_output**: Directories for storing analysis output plots and pickled variables.

# How to run:

## Option 1: Using NetLogo graphical interface

### Requirements

 - Install [NetLogo](https://ccl.northwestern.edu/netlogo/download.shtml) software
	
### Run:

Open NetLogo GUI and use the following steps:

File -> open -> select densityFeedback.nlogo file

On the interface tab, click on setup button to initialise grid, then click on the go "forever" button to run the model. For a quick tutorial on NetLogo models please see https://ccl.northwestern.edu/netlogo/docs/tutorial1.html

Model parameters and simulation duration are defined in the `config.nls` file (See configuration parameters)	  

## Option 2:  Using the command line:
### Requirements

 - Install [NetLogo](https://ccl.northwestern.edu/netlogo/download.shtml) software
 - Install [Java](https://www.java.com/en/download/help/download_options.html)

NetLogo offers command line usage by using the included command line script. This is found in the root directory of your NetLogo installation and is named `netlogo-headless.sh` on Mac and Linux and `netlogo-headless.bat` on Windows. 

The netlogo-headless script expects the following required arguments:

 - `--model <path>`: model path
 - `--experiment <name>`: name of experiment

The experiment setups for the SP spatial models have been already created and are saved in the model files.

Grid dimensions can be also set using the following arguments:

 - `--min-pxcor <number>`
 - `--max-pxcor <number>`
 - `--min-pycor <number>`
 - `--max-pycor <number>`

The following commands demonstrate how to run the SP spatial models in headless mode on Windows with NetLogo 6.1.1 installation, using a grid size of 100 x 100:

<ins>**Downstream model:**</ins>

    $ cd path/to/netlogo/installation/directory (e.g. C:\Program Files\NetLogo 6.1.1\app) 
    $ java -Dfile.encoding=UTF-8 -cp netlogo-6.1.1.jar org.nlogo.headless.Main --model /path/to/downstream/model/densityFeedback.nlogo --experiment densityFeedback --max-pxcor 99 --min-pxcor 0 --max-pycor 99 --min-pycor 0

<ins>**Upstream model:**</ins>
    
    $ cd path/to/netlogo/installation/directory (e.g. /c/Program Files/NetLogo 6.1.1/app)
    $ java -Dfile.encoding=UTF-8 -cp netlogo-6.1.1.jar org.nlogo.headless.Main --model /path/to/upstream/model/densityFeedback.nlogo --experiment upstream --max-pxcor 99 --min-pxcor 0 --max-pycor 99 --min-pycor 0

<ins>**Unified model:**</ins>

    $ cd path/to/netlogo/installation/directory (e.g. /c/Program Files/NetLogo 6.1.1/app)
    $ java -Dfile.encoding=UTF-8 -cp netlogo-6.1.1.jar org.nlogo.headless.Main --model /path/to/unified/model/densityFeedback.nlogo --experiment unified --max-pxcor 99 --min-pxcor 0 --max-pycor 99 --min-pycor 0

For more information and examples on how to run NetLogo in headless mode see https://ccl.northwestern.edu/netlogo/docs/behaviorspace.html#advanced-usage

# Configuration Parameters:	
	
Model and simulation parameters can be set in the `config.nls` file. This may be opened using your prefered text editor or directly in the NetLogo environment. To open it in NetLogo click on the **Included Files** menu (`SP_essentials.nls` should be opened first). The `config.nls` file contains the following variables:

- `model`: model name
- `generate_views`: set to true to generate and store grid images per week (Default: True)
- `generate_world`: set to true to generate and store grid state per week in csv format (Default: False)
- `predefinedSeed`: set to zero for random seed. Set to a specific value for reproducibility
- `sims-duration`: simulation time in weeks
- `division-bias`: set to true to constrain divisions along a single axis (for oesophageal simulations)
- `diffusion`: set to true for allowing an extended neighbourhood	
- `r`: probability of symmetric division (rWT, rMUT in upstream and unified models where mutant and WT cells have distinct symmetric division probabilities)
- `lambda`: division rate (lambdaWT, lambdaMUT in upstream and unified models where mutant and WT cells have distinct division rates)
- `gamma`: stratification rate (gammaWT, gammaMUT in upstream and unified models where mutant and WT cells have distinct stratification rates)
- `delta`: fate imbalance parameter of mutant cells (min:0, max:1) - p53delta and notchdelta in unified model
- `densityBias`: set to true to enable cell density dependent feedbacks
- `crowdingCutOff`: number of neighbours above which the neighbourhood is considered "crowded"
- `immediate-stratification`: true for enabling crowding release, induced by the double state cells (see main text)
- `induction`: proportion of mutant cells to be introduced (set to 0 for wild-type tissue simulations)
- `induction-time`: time (in weeks) when mutant cells are introduced 
- `fdelta`: neighbourhood density feedback bias in fate decision (min:0, max:1) - in upstream and unified models
- `visualize-clones`: set to true to colorise distinct clones instead of cell types. Mutant and wild type cells are not distiguished in this colouring scheme. 

# Grid visualisation colour schemes:

The SP spatial models have the following colouring schemes:

- Downstream model: 
  - WT proliferating cells: yellow 
  - WT differentiating cells: blue 
  - WT double occupancies: green
  - p53 mutants: grey 
  - p53 mutants' double occupancies: black
  - empty spaces: white

- Upstream model: 
  - WT proliferating cells: yellow
  - WT differentiating cells: blue 
  - WT double occupancies: green
  - DN_Maml1 mutants: pink
  - DN_Maml1 mutants' double occupancies: red
  - empty spaces: white

- Unified model: 
  - WT cells: yellow
  - p53 mutants: black
  - DN_Maml1 mutants: red
  - empty spaces: white

# Analysis:

### Analysis workflows

- `cellPopulations`: calculates the number of different cell types:
  - proliferating, differentiating 
  - double and empty state agents
  - proportion of mutated cells
- `averageCloneSize`: calculates the average clone size for wild-type and mutant populations
- `cloneSizeDistribution`: calculates the clone size distributions and clone survival for wild-type and mutant populations
- `rho`: calculates the proportion of proliferating cells:
  - within the whole simulated tissue
  - within individual segregated grid areas
- `cellDensity`: calculates cell density (density at the start of the simulation is 100%, an increase above 100% indicates crowding)
  - within the whole simulated tissue
  - within individual segregated grid areas

### Usage

    usage: main.py [-h] -m PATH [-a SINGLE or COMBINATION OF ANALYSIS WORKFLOWS] [{save,use}]                                                
                                                                                                                                         
    This script performs downstream analysis of simulation outputs generated by the spatial single progenitor models.                        
    It takes as input a path to netlogo model file and the name(s) of the required analysis workflow(s).                                     
    If no analysis workflows are given, then the script performs all the available workflows.                                                
    The user may either save the output calculations as pickled files (choosing the 'save' option) OR                                        
    use existing pickled files from previous runs (choosing the 'use' option). This option might be helpful for producing                    
    alternative plots from existing output calculations without repeating the analysis.                                                      
    USAGE EXAMPLES:                                                                                                                          
    main.py -m "path/to/netlogo/model/directory" save (All analysis workflows will be performed)                                             
    main.py -m "path/to/netlogo/model/directory" -a mutantProportion,averageCloneSize save (Only a subset of two workflows will be performed)
    main.py -m "path/to/netlogo/model/directory" use (Existing analysis outputs will be used and be re-plotted)                              
                                                                                                                                         
    positional arguments:                                                                                                                    
      {save,use}            save output analysis variables (save) or use already saved output variables (use)

    optional arguments:
      -h, --help            show this help message and exit
      -a SINGLE or COMBINATION OF ANALYSIS WORKFLOWS , --analysis SINGLE or COMBINATION OF ANALYSIS WORKFLOWS
                        analysis workflow(s), Choose one or a combination of the following: ['cloneSizeDistribution', 'averageCloneSize', 'cellPopulations', 'cloneInteractions', 'cellDensity', 'rho'],     
                        DEFAULT:['cloneSizeDistribution', 'averageCloneSize', 'cellPopulations', 'cloneInteractions', 'cellDensity', 'rho']

    Required named arguments:
      -m PATH, --model_dir PATH
                        directory containing the model file (.nlogo)