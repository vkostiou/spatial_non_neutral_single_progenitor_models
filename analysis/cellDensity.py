from essentials import *
import os

def plot_cell_density_per_week(cellDensityPerWeek, c):
    numberOfweeks = len(cellDensityPerWeek)
    avgCellDensity = []
    std = []

    weeks = range(numberOfweeks)

    for week in weeks:
        avgCellDensity.append(np.array(cellDensityPerWeek[week]).mean())
        std.append(np.array(cellDensityPerWeek[week]).std())

    d = {
        'data': {
            'x': {'CA model': weeks},
            'y': {
                'CA model': (avgCellDensity, 'k--', std, '#1B2ACC', '#089FFF', 'shaded'),
            },
        },
        'xlabel': 'Weeks',
        'ylabel': 'Density %',
        'title': "Tissue cell density",
        'savefig': c['analysis_output'] + "cell_density_std.png"
    }

    plot(d)


def plot_local_cell_density(localCellDensityPerWeek, c):
    fig, ax = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True)
    fig.suptitle("Local Cell Density")

    ax[0, 0].hist(np.array(localCellDensityPerWeek[10]), edgecolor='gray')
    ax[0, 0].set_title('week 10')
    ax[0, 1].hist(np.array(localCellDensityPerWeek[30]), edgecolor='gray')
    ax[0, 1].set_title('week 30')
    ax[1, 0].hist(np.array(localCellDensityPerWeek[50]), edgecolor='gray')
    ax[1, 0].set_title('week 50')
    ax[1, 1].hist(np.array(localCellDensityPerWeek[70]), edgecolor='gray')
    ax[1, 1].set_title('week 70')
    for a in ax.flat:
        a.set(xlabel='% local density', ylabel='frequency')
    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for a in ax.flat:
        a.label_outer()

    plt.savefig(c['analysis_output'] + "local_density_hist.png", dpi=300)
    plt.close()


def cellDensityPerWeek(c, options):
    cellDensityPerWeek = {}
    localCellDensityPerWeek = {}

    if options.var == 'use':
        cellDensityPerWeek = readVariableFromDisk('cellDensityPerWeek', c)
        localCellDensityPerWeek = readVariableFromDisk('localCellDensityPerWeek', c)
    else:
        for filename in os.listdir(c['netlogo_output']):
            [week, seed] = re.findall(r"[-]?\d+|\d+", filename)

            week = int(week)
            agents = parse_netlogo_world(c['netlogo_output'] + filename)

            cellDensityPerWeek.setdefault(week, [])
            globalDensity = (get_num_of_cells(agents) / agents.shape[0]) * 100
            cellDensityPerWeek[week].append(globalDensity)

            if week == 10 or week == 30 or week == 50 or week == 70:  # week % 20 == 0 and week !=0:
                chunks = get_grid_chunks(agents)  # split grid to smaller sections
                localCellDensityPerWeek.setdefault(week, [])
                chunkSize = chunks[0].shape[0]
                for chunk in chunks:
                    localDensity = (get_num_of_cells(chunk) / chunkSize) * 100
                    localCellDensityPerWeek[week].append(localDensity)

    if options.var == 'save':
        writeVariableToDisk(cellDensityPerWeek, 'cellDensityPerWeek', c)
        writeVariableToDisk(localCellDensityPerWeek, 'localCellDensityPerWeek', c)

    plot_cell_density_per_week(cellDensityPerWeek, c)
    plot_local_cell_density(localCellDensityPerWeek, c)
