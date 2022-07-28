from essentials import *
import os


def plotAvgCloneSizePerWeek(totalCloneSizePerWeek, cloneType, c):
    numberOfweeks = len(totalCloneSizePerWeek)
    avgCloneSizesPerWeek = []
    std = []

    weeks = range(numberOfweeks)

    for week in weeks:
        avgCloneSizesPerWeek.append(np.array(totalCloneSizePerWeek[week]).mean())
        std.append(np.array(totalCloneSizePerWeek[week]).std())


    d = {
        'data': {
            'x': {
                'CA model': weeks,
            },
            'y': {
                'CA model': (avgCloneSizesPerWeek, 'ko', std, '#1B2ACC', '#089FFF', 'shaded'),
            },
        },
        'xlabel': 'Weeks',
        'ylabel': 'Average clone size',
        'title': cloneType +" average clone size over time",
        'savefig': c['analysis_output'] + cloneType + "_average_clone_size_per_week_std.png"
    }

    plot(d)

def avgCloneSizePerWeek(c, options):
    if c['induction_level'] > 0:
        totalMutCloneSizePerWeek = {}
        totalWTCloneSizePerWeek = {}

        if options.var == 'use':
            totalMutCloneSizePerWeek = readVariableFromDisk('totalMutCloneSizePerWeek', c)
            totalWTCloneSizePerWeek = readVariableFromDisk('totalWTCloneSizePerWeek', c)
        else:
            for filename in os.listdir(c['netlogo_output']):
                [week, seed] = re.findall(r"[-]?\d+|\d+", filename)

                week = int(week)
                agents = parse_netlogo_world(c['netlogo_output'] + filename)
                clones = get_clones(agents)  # group agents by clone ID

                totalWTCloneSizePerWeek.setdefault(week, [])

                mutantClones, wtClones = split_clones(clones)

                for mutant, mclones in mutantClones.items():

                    totalMutCloneSizePerWeek.setdefault(mutant, {}).setdefault(week, [])

                    for cloneID, cloneAgents in mclones.items():
                        totalMutCloneSizePerWeek[mutant][week].append(get_num_of_cells(cloneAgents))

                for cloneID, cloneAgents in wtClones.items():
                    totalWTCloneSizePerWeek[week].append(get_num_of_cells(cloneAgents))

        if options.var == 'save':
            writeVariableToDisk(totalMutCloneSizePerWeek, 'totalMutCloneSizePerWeek', c)
            writeVariableToDisk(totalWTCloneSizePerWeek, 'totalWTCloneSizePerWeek', c)

        plotAvgCloneSizePerWeek(totalWTCloneSizePerWeek, "WT", c)

        for mutant, cloneSizePerWeek in totalMutCloneSizePerWeek.items():
            plotAvgCloneSizePerWeek(totalMutCloneSizePerWeek[mutant], mutant, c)

    else:
        totalCloneSizePerWeek = {}

        if options.var == 'use':
            totalCloneSizePerWeek = readVariableFromDisk('totalCloneSizePerWeek', c)
        else:
            for filename in os.listdir(c['netlogo_output']):
                [week, seed] = re.findall(r"[-]?\d+|\d+", filename)

                week = int(week)
                agents = parse_netlogo_world(c['netlogo_output'] + filename)
                clones = get_clones(agents)  # group agents by clone ID

                totalCloneSizePerWeek.setdefault(week, [])
                for cloneID, cloneAgents in clones.items():
                    totalCloneSizePerWeek[week].append(get_num_of_cells(cloneAgents))

        if options.var == 'save':
            writeVariableToDisk(totalCloneSizePerWeek, 'totalCloneSizePerWeek', c)

        plotAvgCloneSizePerWeek(totalCloneSizePerWeek, "WT", c)
