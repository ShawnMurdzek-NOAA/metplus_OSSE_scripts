# MET Plotting Utility

To run:

0. Run METplus to create MET output.
1. Create a run directory.
2. Create an input YAML file in your run directory (see examples in `test/cases/plots/*/plot_param.yml`).
3. Copy `run_MET_plots.sh` to your run directory.
4. Edit `run_MET_plots.sh` based on the machine you are using.
5. Submit a batch job to run the plotting program: `sbatch run_MET_plots.sh`.
