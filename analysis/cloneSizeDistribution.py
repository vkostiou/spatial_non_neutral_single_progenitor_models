from essentials import *
import seaborn as sns
import os

def plot_distributions(data, yaxis, c, type="WT"):

    df = pd.DataFrame(data)
    df = df.loc[df['week'].apply(lambda x: x % 20 == 0 and x != 0)]

    box = sns.boxplot(x='week', y=yaxis, data=df)
    plt.title(type)
    plt.xlabel('Week')
    plt.ylabel('Clone size')
    plt.savefig(c['analysis_output'] + "boxplot_" + type + "_clone_size.png", dpi=300)
    plt.close()

def plotCloneSurvivalPerWeek(numOfClonesPerWeek, cloneType, c):
    numberOfweeks = len(numOfClonesPerWeek)
    avgCloneSurvPerWeek = []
    std = []

    weeks = range(numberOfweeks)

    for week in weeks:
        avgCloneSurvPerWeek.append(np.array(numOfClonesPerWeek[week]).mean())
        std.append(np.array(numOfClonesPerWeek[week]).std())

    d = {
        'data': {
            'x': {
                cloneType + ' model': weeks,
            },
            'y': {
                cloneType + ' model': (avgCloneSurvPerWeek, 'b-', std, '#1B2ACC', '#089FFF', 'shaded'),
            },
        },
        'xlabel': 'Weeks',
        'ylabel': 'Number of clones',
        'title': cloneType +" surviving clones over time",
        'savefig': c['analysis_output'] + cloneType + "average_clone_surv_per_week_std.png"
    }

    plot(d)


def cloneSizeDistributionPerWeek (c, options):
    if c['induction_level'] > 0:

        mutCloneSizes = {}
        wtCloneSizes = []
        MUTnumberOfClones = {}
        WTnumberOfClones = {}

        if options.var == 'use':
            mutCloneSizes = readVariableFromDisk('mutCloneSizes', c)
            wtCloneSizes = readVariableFromDisk('wtCloneSizes', c)
            MUTnumberOfClones = readVariableFromDisk('MUTnumberOfClones', c)
            WTnumberOfClones = readVariableFromDisk('WTnumberOfClones', c)
        else:
            for filename in os.listdir(c['netlogo_output']):
                [week, seed] = re.findall(r"[-]?\d+|\d+", filename)

                week = int(week)
                agents = parse_netlogo_world(c['netlogo_output'] + filename)
                clones = get_clones(agents)  # group agents by clone ID
                mutantClones, wtClones = split_clones(clones)

                WTnumberOfClones.setdefault(week, [])
                WTnumberOfClones[week].append(len(wtClones))

                for cloneID, cloneAgents in wtClones.items():
                    wtCloneSizes.append({"week": week, "wt_clone_size": get_num_of_cells(cloneAgents)})
                for mutant, mclones in mutantClones.items():

                    mutCloneSizes.setdefault(mutant, [])
                    MUTnumberOfClones.setdefault(mutant, {}).setdefault(week,[])
                    MUTnumberOfClones[mutant][week].append(len(mclones))

                    for cloneID, cloneAgents in mclones.items():
                        mutCloneSizes[mutant].append({"week": week, "mutant_clone_size": get_num_of_cells(cloneAgents)})

        if options.var == 'save':
            writeVariableToDisk(mutCloneSizes, 'mutCloneSizes', c)
            writeVariableToDisk(wtCloneSizes, 'wtCloneSizes', c)
            writeVariableToDisk(MUTnumberOfClones, 'MUTnumberOfClones', c)
            writeVariableToDisk(WTnumberOfClones, 'WTnumberOfClones', c)

        for mutant in mutCloneSizes.keys():
            plot_distributions(mutCloneSizes[mutant], 'mutant_clone_size', c, mutant)
            plotCloneSurvivalPerWeek(MUTnumberOfClones[mutant], mutant, c)
        plot_distributions(wtCloneSizes, 'wt_clone_size', c)
        plotCloneSurvivalPerWeek(WTnumberOfClones, "WT", c)


    else:
        cloneSizes = []
        numberOfClones = {}

        if options.var == 'use':
            cloneSizes = readVariableFromDisk('cloneSizes', c)
            numberOfClones = readVariableFromDisk('numberOfClones', c)
        else:
            for filename in os.listdir(c['netlogo_output']):
                [week, seed] = re.findall(r"[-]?\d+|\d+", filename)

                week = int(week)
                agents = parse_netlogo_world(c['netlogo_output'] + filename)
                clones = get_clones(agents)  # group agents by clone ID

                numberOfClones.setdefault(week, [])
                numberOfClones[week].append(len(clones))

                if week % 20 == 0 and week !=0:
                    for cloneID, cloneAgents in clones.items():
                        cloneSizes.append({"week": week, "wt_clone_size": get_num_of_cells(cloneAgents)})

        if options.var == 'save':
            writeVariableToDisk(cloneSizes, 'cloneSizes', c)
            writeVariableToDisk(numberOfClones, 'numberOfClones', c)

        plot_distributions(cloneSizes,'wt_clone_size', c)
        plotCloneSurvivalPerWeek(numberOfClones, "WT", c)
