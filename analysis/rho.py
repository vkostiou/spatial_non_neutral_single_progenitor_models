from essentials import *
import os


def plot_rho_per_week(rhoPerWeek, c):
    numberOfweeks = len(rhoPerWeek)
    avgRho = []
    std = []

    weeks = range(numberOfweeks)

    for week in weeks:
        avgRho.append(np.array(rhoPerWeek[week]).mean())
        std.append(np.array(rhoPerWeek[week]).std())

    d = {
        'data': {
            'x': {'CA model': weeks},
            'y': {
                'CA model': (avgRho, 'k--', std, '#1B2ACC', '#089FFF', 'shaded'),
            },
        },
        'xlabel': 'Weeks',
        'ylabel': 'rho',
        'title': "Proportion of proliferating cells",
        'savefig': c['analysis_output'] + "rho_std.png"
    }

    plot(d)


def plot_local_rho(localRhoPerWeek, c):
    fig, ax = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True)
    fig.suptitle("Local rho")

    ax[0, 0].hist(np.array(localRhoPerWeek[10]), edgecolor='gray')
    ax[0, 0].set_title('week 10')
    ax[0, 1].hist(np.array(localRhoPerWeek[30]), edgecolor='gray')
    ax[0, 1].set_title('week 30')
    ax[1, 0].hist(np.array(localRhoPerWeek[50]), edgecolor='gray')
    ax[1, 0].set_title('week 50')
    ax[1, 1].hist(np.array(localRhoPerWeek[70]), edgecolor='gray')
    ax[1, 1].set_title('week 70')
    for a in ax.flat:
        a.set(xlabel='local rho', ylabel='frequency')
    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for a in ax.flat:
        a.label_outer()

    plt.savefig(c['analysis_output'] + "local_rho_hist.png", dpi=300)
    plt.close()


def rhoPerWeek(c, options):
    rhoPerWeek = {}
    localRhoPerWeek = {}

    if options.var == 'use':
        rhoPerWeek = readVariableFromDisk('rhoPerWeek', c)
        localRhoPerWeek = readVariableFromDisk('localRhoPerWeek', c)
    else:
        for filename in os.listdir(c['netlogo_output']):
            [week, seed] = re.findall(r"[-]?\d+|\d+", filename)

            week = int(week)
            agents = parse_netlogo_world(c['netlogo_output'] + filename)

            rhoPerWeek.setdefault(week, [])
            rho = get_rho(agents)
            rhoPerWeek[week].append(rho)

            if week == 10 or week == 30 or week == 50 or week == 70:  # week % 20 == 0 and week !=0:
                chunks = get_grid_chunks(agents)  # split grid to smaller sections
                localRhoPerWeek.setdefault(week, [])
                chunkSize = chunks[0].shape[0]
                for chunk in chunks:
                    localRho = (get_rho(chunk) / chunkSize) * 100
                    localRhoPerWeek[week].append(localRho)

    if options.var == 'save':
        writeVariableToDisk(rhoPerWeek, 'rhoPerWeek', c)
        writeVariableToDisk(localRhoPerWeek, 'localRhoPerWeek', c)

    plot_rho_per_week(rhoPerWeek, c)
    plot_local_rho(localRhoPerWeek, c)
