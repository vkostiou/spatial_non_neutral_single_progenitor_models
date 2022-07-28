import argparse
import os
import re
import pandas as pd
import networkx as nx
import datetime
import textwrap
import time
import numpy as np
import matplotlib.pyplot as plt
import pickle

'''
Read command line arguments and return list of analysis routines to run
'''

def parse_arguments():
    valid_analysis_names = ['cloneSizeDistribution', 'averageCloneSize', 'cellPopulations', 'cloneInteractions',
                            'cellDensity', 'rho']

    def validate_path(p):
        if not os.path.exists(p):
            error_msg = f"{p} does not exist"
            raise argparse.ArgumentTypeError(error_msg)
        return p

    # check that the analysis routines passed by the user are valid
    def validate_analysis_workflows(analysis_workflows):
        analysis_workflows = analysis_workflows.split(',')
        for analysis_workflow in analysis_workflows:
            if analysis_workflow not in valid_analysis_names:
                error_msg = f'{analysis_workflow} is not a valid analysis workflow. Choose one or a combination of the following workflows: {valid_analysis_names}'
                raise argparse.ArgumentTypeError(error_msg)
        return analysis_workflows

    description = textwrap.dedent('''
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
    ''')
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=description)
    requiredNamed = parser.add_argument_group('Required named arguments')
    requiredNamed.add_argument('-m', '--model_dir', help='directory containing the model file (.nlogo)',
                        required=True, type=validate_path, metavar='PATH')
    parser.add_argument('-a', '--analysis', help=f'analysis workflow(s), Choose one or a combination of the following: {valid_analysis_names}, DEFAULT:{valid_analysis_names}',
                        type=validate_analysis_workflows, default=','.join(valid_analysis_names), metavar='SINGLE or COMBINATION OF ANALYSIS WORKFLOWS ')
    parser.add_argument('var', help='save output analysis variables (save) or use already saved output variables (use)',
                        nargs='?', choices=('save', 'use'))

    args = parser.parse_args()

    return args


'''
Read config files and return dictionary with config values
'''


def parse_config_files(netlogo_conf):
    config_values = {}

    # read netlogo config
    with open(netlogo_conf, "r") as f:
        for line in f:
            weeks_pattern = re.search("set sims-duration (\d+)", line)
            induction_pattern = re.search("set induction (\d+\.?\d*)", line)
            if weeks_pattern:
                config_values.setdefault("weeks", int(weeks_pattern.group(1)))
            if induction_pattern:
                config_values.setdefault("induction_level", float(induction_pattern.group(1)))
    return config_values


'''
Convert string of neighbors to list of neighbors
'''


def parse_neighbors_string(string):
    # "{turtles 26 48 43 39 33 91}"

    neighbors = string.split(' ')
    # ["{turtles","26","48","43","39","33","91}"]
    neighbors.pop(0)
    # ["26","48","43","39","33","91}"]
    neighbors[-1] = neighbors[-1][:-1]
    # ["26","48","43","39","33","91"]
    neighbors = [int(n) for n in neighbors]
    # [26,48,43,39,33,91]

    return neighbors


'''
Parse netlogo world csv and return dataframe with selected fields
'''


def parse_netlogo_world(csv):
    # Keep only rows corresponding to "turtle" agents
    top_rows_to_exclude = 0
    bottom_rows_to_exclude = 0
    with open(csv) as f:
        for i, l in enumerate(f):
            if l.startswith("\"TURTLES\""):
                top_rows_to_exclude = i + 1
            if l.startswith("\"PATCHES\""):
                bottom_rows_to_exclude = i - 1

    df = pd.read_csv(csv, skiprows=top_rows_to_exclude, nrows=bottom_rows_to_exclude - top_rows_to_exclude - 1)
    df = df.loc[:, ["who", "xcor", "ycor", "six-neighbors", "cell-type", "state", "time", "cloneid", "creation-time",
                    "mutation-status", "fate-bias"]]

    # certain csv columns are triple quoted, extra quotes have to be removed
    for column in ["cell-type", "state", "mutation-status"]:
        df[column] = df[column].apply(lambda x: x.replace('"', ''))

    # convert string of neighbors to list of neighbors
    df["six-neighbors"] = df["six-neighbors"].apply(lambda x: parse_neighbors_string(x))

    return df


'''
Return dataframe containing neighbors
'''


def get_neighbors(agent, agents):

    neighbors = agents[agents['who'].isin(agent["six-neighbors"])]
    return neighbors


'''
Parse netlogo events csv and return tuple with either division or stratification events for mutants and WT cells
'''


def parse_netlogo_events(csv):
    df = pd.read_csv(csv, header=None)

    mutant = {}
    wildType = {}

    pat = re.compile('array: ([\d\s]+)')
    for row_index, row in df.iterrows():
        mo = pat.findall(row[1])
        mut = [int(n) for n in mo[0].split(' ')]
        wt = [int(n) for n in mo[1].split(' ')]

        for i in range(len(mut)):
            mutant.setdefault(i, [])
            wildType.setdefault(i, [])

            mutant[i].append(mut[i])
            wildType[i].append(wt[i])

    return (mutant, wildType)



'''
Group agents by clone id and return dictionary with key: cloneID and value: dataframe with clone members
'''


def get_clones(agents):
    # ignore clones with ID = 0 (i.e ignore empty agents and initial B agents)
    agents = agents[agents["cloneid"] != 0]

    # create empty dataframe for every clone ID key
    cloneIDs = agents['cloneid'].unique()
    clones = {elem: pd.DataFrame for elem in cloneIDs}

    # populate clone dataframes and reset their index
    for cloneID in clones.keys():
        clones[cloneID] = agents[agents['cloneid'] == cloneID].reset_index(drop=True)

    return clones


'''
Segregate grid to smaller sections and return list of dataframes
'''


def get_grid_chunks(agents):
    chunks = []

    # This is for square dimensional grid only
    grid_side = int(agents.shape[0] ** (1 / 2))  # .shape[0] returns number of dataframe rows (total number of agents)
    chunk_side = int(grid_side / 10)

    # Create chunks according to chunk_side
    for x in range(0, grid_side, chunk_side):
        for y in range(0, grid_side, chunk_side):
            xmax = x + chunk_side
            ymin = y - 0.5
            ymax = y + chunk_side - 0.5
            chunk = agents[
                (agents['xcor'] >= x) & (agents['xcor'] < xmax) & (agents['ycor'] >= ymin) & (agents['ycor'] < ymax)]
            chunks.append(chunk)

    return chunks


'''
Count number of epithelial cells for a given group of agents
'''


def get_num_of_cells(groupOfAgents):
    numOfsingle = groupOfAgents[groupOfAgents["state"] == "single"].shape[0]
    numOfdouble = groupOfAgents[groupOfAgents["state"] == "double"].shape[0]

    return numOfdouble * 2 + numOfsingle


'''
Count cell populations
'''


def get_cell_populations(groupOfAgents):
  numOfAlpha = groupOfAgents[groupOfAgents["cell-type"] == "A"].shape[0]
  numOfAlpha += (groupOfAgents[groupOfAgents["cell-type"] == "AA"].shape[0]) * 2
  numOfAlpha += groupOfAgents[groupOfAgents["cell-type"] == "AB"].shape[0]
  numOfAlpha += groupOfAgents[groupOfAgents["cell-type"] == "BA"].shape[0]

  numOfBeta = groupOfAgents[groupOfAgents["cell-type"] == "B"].shape[0]
  numOfBeta += (groupOfAgents[groupOfAgents["cell-type"] == "BB"].shape[0]) * 2
  numOfBeta += groupOfAgents[groupOfAgents["cell-type"] == "AB"].shape[0]
  numOfBeta += groupOfAgents[groupOfAgents["cell-type"] == "BA"].shape[0]

  numOfDouble = groupOfAgents[groupOfAgents["state"] == "double"].shape[0]

  numOfEmpty = groupOfAgents[groupOfAgents["state"] == "empty"].shape[0]

  return [numOfAlpha, numOfBeta, numOfDouble, numOfEmpty]


'''
Calculate rho for a given group of agents
'''


def get_rho(groupOfAgents):
    numOfAlpha = groupOfAgents[groupOfAgents["cell-type"] == "A"].shape[0]
    numOfAlpha += (groupOfAgents[groupOfAgents["cell-type"] == "AA"].shape[0]) * 2
    numOfAlpha += groupOfAgents[groupOfAgents["cell-type"] == "AB"].shape[0]
    numOfAlpha += groupOfAgents[groupOfAgents["cell-type"] == "BA"].shape[0]

    numOfBeta = groupOfAgents[groupOfAgents["cell-type"] == "B"].shape[0]
    numOfBeta += (groupOfAgents[groupOfAgents["cell-type"] == "BB"].shape[0]) * 2
    numOfBeta += groupOfAgents[groupOfAgents["cell-type"] == "AB"].shape[0]
    numOfBeta += groupOfAgents[groupOfAgents["cell-type"] == "BA"].shape[0]

    return numOfAlpha / (numOfAlpha + numOfBeta)


'''
Return if a clone is fragmented or not
'''


def is_fragmented(cloneGraph):
    return not nx.is_connected(cloneGraph)


'''
Create epithelial cell adjacency list for a given clone
'''


def get_clone_adjacencies(cloneAgents):
    adjacencies = {}

    for index, agent1 in cloneAgents.iterrows():
        if agent1["state"] == "single":
            adjacencies.setdefault(str(agent1["who"]), [])
            for index, agent2 in cloneAgents.iterrows():
                if agent2["who"] in agent1["six-neighbors"]:
                    if agent2["state"] == "single":
                        adjacencies[str(agent1["who"])].append(str(agent2["who"]))
                    elif agent2["state"] == "double":
                        adjacencies[str(agent1["who"])].append(str(agent2["who"]) + 'a')
                        adjacencies[str(agent1["who"])].append(str(agent2["who"]) + 'b')
        elif agent1["state"] == "double":
            adjacencies.setdefault(str(agent1["who"]) + 'a', [])
            adjacencies.setdefault(str(agent1["who"]) + 'b', [])
            for index, agent2 in cloneAgents.iterrows():
                if agent2["who"] in agent1["six-neighbors"]:
                    if agent2["state"] == "single":
                        adjacencies[str(agent1["who"]) + 'a'].append(agent2["who"])
                        adjacencies[str(agent1["who"]) + 'b'].append(agent2["who"])
                    elif agent2["state"] == "double":
                        adjacencies[str(agent1["who"]) + 'b'].append(str(agent2["who"]) + 'a')
                        adjacencies[str(agent1["who"]) + 'a'].append(str(agent2["who"]) + 'a')
                        adjacencies[str(agent1["who"]) + 'a'].append(str(agent2["who"]) + 'b')
                        adjacencies[str(agent1["who"]) + 'b'].append(str(agent2["who"]) + 'b')

    return adjacencies


'''
Create clone graph
'''


def get_clone_graph(cloneAgents):
    adjacencies = get_clone_adjacencies(cloneAgents)
    graph = nx.Graph(adjacencies)

    return graph


'''
Create adjacency list for automaton cells (different to biological cells)
'''


def get_adjacencies(agents):
    adjacencies = {}

    for index, agent1 in agents.iterrows():
        adjacencies.setdefault(str(agent1["who"]), [])
        for index, agent2 in agents.iterrows():
            if agent2["who"] in agent1["six-neighbors"]:
                adjacencies[str(agent1["who"])].append(str(agent2["who"]))

    return adjacencies


'''
Create graph for an agent list
'''


def get_graph(agents):
    adjacencies = get_adjacencies(agents)
    graph = nx.Graph(adjacencies)

    return graph


def log(log_file, analysis_name):
    with open(log_file, "a") as logger:
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y/%m/%d %H:%M:%S')
        message = analysis_name + ' DONE'
        logger.write(timestamp + ' ' + message + "\n")


def get_mutant_percentage(groupOfAgents, mutantType):
    groupOfmutants = groupOfAgents[groupOfAgents["mutation-status"] == mutantType]
    numOfmutants = get_num_of_cells(groupOfmutants)
    numOfTotalCells = get_num_of_cells(groupOfAgents)

    return (numOfmutants / numOfTotalCells) * 100


def plot(d):

    # {
    #     'data': {
    #         'x': {
    #              'label1': [],
    #              'label2': [],
    #          },
    #         'y': {
    #             'label1': ([], 'formatString', [], 'edgecolor', 'facecolor'),
    #             'label2': ([], 'formatString', [], 'edgecolor', 'facecolor'),
    #             'label3': ([], 'formatString', [], 'edgecolor', 'facecolor'),
    #         },
    #     },
    #     'xlabel': '',
    #     'ylabel': '',
    #     'title': '',
    #     'savefig': ''
    # }

    x = d['data']['x']
    #plt.rcParams.update({'font.size': 12})
    for label, (y, format, std, ec, fc, errormode) in d['data']['y'].items():
        std = np.array(std)
        plt.plot(x[label], y, format, label=label, markersize=3)
        if std.size > 0:
            if errormode == 'shaded':
                plt.fill_between(x[label], y - std, y + std, alpha=0.1, edgecolor=ec, facecolor=fc, linewidth=0)
            if errormode == 'bar':
                plt.errorbar(x[label], y, yerr=std, linestyle="None", elinewidth=0.5, ecolor='red', capsize=3, capthick=0.5)
                #ax.errorbar(x, means, yerr=stdev, color='red', ls='--', marker='o', capsize=5, capthick=1, ecolor='black')

    plt.ylabel(d['ylabel'])
    plt.xlabel(d['xlabel'])
    plt.title(d['title'])
    plt.axis()
    if len(d['data']['y']) > 1:
        plt.legend()
    plt.ylim(0)
    plt.savefig(d['savefig'], dpi=300)
    plt.close()


def split_clones(clones):
    mutants = {}
    wt = {}

    for cloneID, cloneAgents in clones.items():
        mutation_status = cloneAgents.loc[0, "mutation-status"]
        if mutation_status == "WT":
            wt.setdefault(cloneID, pd.DataFrame)
            wt[cloneID] = cloneAgents
        if mutation_status == "p53":
            mutants.setdefault("p53", {}).setdefault(cloneID, pd.DataFrame)
            mutants["p53"][cloneID] = cloneAgents
        if mutation_status == "N":
            mutants.setdefault("N", {}).setdefault(cloneID, pd.DataFrame)
            mutants["N"][cloneID] = cloneAgents

    return [mutants, wt]


def writeVariableToDisk(variable,variableName,config):
    fh = open(config['analysis_output'] + "/dump_vars/" + variableName, 'wb')
    pickle.dump(variable, fh)


def readVariableFromDisk(variableName,config):
    fh=open(config['analysis_output'] + "/dump_vars/" + variableName, 'rb')
    return pickle.load(fh)