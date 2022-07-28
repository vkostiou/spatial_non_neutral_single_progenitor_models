import matplotlib.pyplot as plt
plt.switch_backend('agg')
from averageCloneSize import *
from mutantProportion import *
from cellDensity import *
from rho import *
from cloneSizeDistribution import *
from cellPopulations import *


def main():
    # options = parse_command_line_arguments(sys.argv[1:])
    options = parse_arguments()
    # analysisToRun = options['analysisToRun']
    analysisToRun = options.analysis

    # netlogo_model_dir = options['model_dir']
    netlogo_model_dir = options.model_dir
    netlogo_config = os.path.join(netlogo_model_dir, "config.nls")

    log_file = os.path.join(netlogo_model_dir, "log")
    c = parse_config_files(netlogo_config)
    c['netlogo_output'] = os.path.join(netlogo_model_dir, "netlogo_output", "worlds/")
    c['analysis_output'] = os.path.join(netlogo_model_dir, "analysis_output/")

    if 'averageCloneSize' in analysisToRun:
        avgCloneSizePerWeek(c, options)
        log(log_file, 'averageCloneSize')

    if 'cellPopulations' in analysisToRun:
        mutantPercentagePerWeek(c, options)
        log(log_file, 'mutantPercentage')
        cellPopulationsPerWeek(c, options)
        log(log_file, 'cellPopulations')

    if 'cellDensity' in analysisToRun:
        cellDensityPerWeek(c, options)
        log(log_file, 'cellDensity')

    if 'rho' in analysisToRun:
        rhoPerWeek(c, options)
        log(log_file, 'rho')

    if 'cloneSizeDistribution' in analysisToRun:
        cloneSizeDistributionPerWeek(c, options)
        log(log_file, 'cloneSizeDistribution')


if __name__ == "__main__":
    main()

