from essentials import *
import os


def plot_mutant_percentage_per_week(mutantPercentagePerWeek, c):
    for mutationStatus, percentagePerWeek in mutantPercentagePerWeek.items():

        weeks = list(sorted(percentagePerWeek.keys()))

        avgMutantPercentage = []
        std = []

        for week in weeks:
            avgMutantPercentage.append(np.array(percentagePerWeek[week]).mean())
            std.append(np.array(percentagePerWeek[week]).std())

        d = {
            'data': {
                'x': {'CA model': weeks,

                },
                'y': {
                    'CA model': (avgMutantPercentage, 'k--', std, '#1B2ACC', '#089FFF', 'shaded'),
                },
            },
            'xlabel': 'Weeks',
            'ylabel': '% Proportion of ' + mutationStatus + ' cells',
            'title': "Tissue take over",
            'savefig': c['analysis_output'] + mutationStatus + "percentage_std.png"
        }

        plot(d)


def mutantPercentagePerWeek(c, options):
    mutantPercentagePerWeek = {}

    if options.var == 'use':
        mutantPercentagePerWeek = readVariableFromDisk('mutantPercentagePerWeek', c)
    else:
        for filename in os.listdir(c['netlogo_output']):
            [week, seed] = re.findall(r"[-]?\d+|\d+", filename)

            week = int(week)
            agents = parse_netlogo_world(c['netlogo_output'] + filename)

            mutantTypes = agents["mutation-status"].unique()

            for mt in mutantTypes:
                if mt != "0":  # Ignore empties
                    mutantPercentagePerWeek.setdefault(mt, {}).setdefault(week, [])
                    mutantPercentagePerWeek[mt][week].append(get_mutant_percentage(agents, mt))

    if options.var == 'save':
        writeVariableToDisk(mutantPercentagePerWeek, 'mutantPercentagePerWeek', c)

    plot_mutant_percentage_per_week(mutantPercentagePerWeek, c)
