from essentials import *
import os


def plotCellPopulationsPerWeek(cellPopulations, c):
    numberOfweeks = len(cellPopulations)

    avgAlpha = []
    stdAlpha = []
    avgBeta = []
    stdBeta = []
    avgDouble = []
    stdDouble = []
    avgEmpty = []
    stdEmpty = []

    weeks = range(numberOfweeks)

    for week in weeks:
        avgAlpha.append(np.array(cellPopulations[week]['A']).mean())
        stdAlpha.append(np.array(cellPopulations[week]['A']).std())
        avgBeta.append(np.array(cellPopulations[week]['B']).mean())
        stdBeta.append(np.array(cellPopulations[week]['B']).std())
        avgDouble.append(np.array(cellPopulations[week]['D']).mean())
        stdDouble.append(np.array(cellPopulations[week]['D']).std())
        avgEmpty.append(np.array(cellPopulations[week]['E']).mean())
        stdEmpty.append(np.array(cellPopulations[week]['E']).std())

    dcells = {
        'data': {
            'x': {
                'Proliferating Cells': weeks,
                'Differentiating Cells': weeks
            },
            'y': {
                'Proliferating Cells': (avgAlpha, 'k-o', stdAlpha, 'black', 'black', 'shaded'),
                'Differentiating Cells': (avgBeta, 'b-o', stdBeta, 'blue', 'blue', 'shaded')
            },
        },
        'xlabel': 'Weeks',
        'ylabel': 'Number of cells',
        'title': " Average population size over time",
        'savefig': c['analysis_output'] + "cell_populations_per_week_std.png"
    }

    plot(dcells)

    dcrowding = {
        'data': {
            'x': {
                'Doubles': weeks,
                'Empties': weeks
            },
            'y': {
                'Doubles': (avgDouble, 'g-o', stdDouble, 'green', 'green', 'shaded'),
                'Empties': (avgEmpty, 'k-o', stdEmpty, 'black', 'black', 'shaded')
            },
        },
        'xlabel': 'Weeks',
        'ylabel': 'Number of cells',
        'title': " Average crowding / extinction events over time",
        'savefig': c['analysis_output'] + "doubles_empties_per_week_std.png"
    }

    plot(dcrowding)


def cellPopulationsPerWeek(c, options):
    cellPopulations = {}

    if options.var == 'use':
        cellPopulations = readVariableFromDisk('cellPopulations', c)
    else:
        for filename in os.listdir(c['netlogo_output']):
            [week, seed] = re.findall(r"[-]?\d+|\d+", filename)

            week = int(week)
            agents = parse_netlogo_world(c['netlogo_output'] + filename)

            cellPopulations.setdefault(week, {}).setdefault('A', [])
            cellPopulations[week]['A'].append(get_cell_populations(agents)[0])

            cellPopulations.setdefault(week, {}).setdefault('B', [])
            cellPopulations[week]['B'].append(get_cell_populations(agents)[1])

            cellPopulations.setdefault(week, {}).setdefault('D', [])
            cellPopulations[week]['D'].append(get_cell_populations(agents)[2])

            cellPopulations.setdefault(week, {}).setdefault('E', [])
            cellPopulations[week]['E'].append(get_cell_populations(agents)[3])

    if options.var == 'save':
        writeVariableToDisk(cellPopulations, 'cellPopulations', c)

    plotCellPopulationsPerWeek(cellPopulations, c)