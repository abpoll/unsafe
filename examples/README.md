# Examples

This subdirectory hosts two examples of worklows that make use of UNSAFE. The purpose of the `examples/phil_frd_partial` example is to introduce the risk estimation workflow UNSAFE is designed to accommodate and demonstrate that the source code does what we say it does in the technical documentation. This example includes two .zip directories in `phil_frd_partial/data/raw/external/`:

1) `../external/haz/dg_clipped.zip`, and
2) `../external/vuln/ddfs.zip`

Because these two datasets are provided for you, you can run all cells in the `phil_frd_partial/notebooks/partial_data_example.ipynb` notebook. The hazard data in the dg_clipped.zip directory is a clipped depth grid from the full data example included in the `philadelphia_frd/` example. This example includes the depth-damage functions .zip directory, but the hazard data is too large to upload to GitHub. To work through the full data example, you may access the hazard data [here](https://doi.org/10.5281/zenodo.15538686). Please download this data and place the `dg.zip` directory in `data/raw/external/haz/` (you will need to create the `haz` subdirectory). You do not have to unzip this, as **UNSAFE** will do this for you. 

You can also test out UNSAFE outside of these examples with your own hazard data in the same county or a different county. To do this, you will need to upload depth-damage functions into a `../data/raw/external/vuln/` subdirectory of your project, which you can download from this [Zenodo repository](https://zenodo.org/records/10027236). We recommend placing your hazard data in `data/raw/external/haz/` as **UNSAFE** uses parts of the subdirectory paths when unzipping data to make it easier to find. 

## Getting ready to run the examples
To run these examples, you will need to have have [conda](https://docs.conda.io/en/latest/) or [mamba](https://mamba.readthedocs.io/en/latest/) installed. Before you head over to the examples and launch the Jupyter notebooks, you will need to follow these steps:

1) Change your working directory to `examples/` and then run `conda env create -f env/environment.yml` or replace `conda` with `mamba`. 
2) Activate the environment.
3) Create an ipykernel for the environment. If you are new to Jupyter Notebooks and/or conda, please see: https://ipython.readthedocs.io/en/stable/install/kernel_install.html#kernels-for-different-environments. We ran `$ python -m ipykernel install --user --name unsafe`
4) Change your working directory back to the root of the cloned UNSAFE repository and run `pip install -e .` so that the unsafe modules can be imported. 

When you go to the Jupyter notebooks to run the examples, make sure you activate the unsafe environment. 

These instructions were successfully followed, and the partial data example was successfully re-executed, on the following system(s):

1) Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-102-generic x86_64) machine with mamba version 1.4.2
2) macOS Sonoma 14.4.1 (Apple M1 Max, 64GB memory) machine with mamba version 1.5.5

These instructions were successfully followed, and the full data example was successfully re-executed, on the following system(s):

1) Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-102-generic x86_64) machine with mamba version 1.4.2

Please check the output of the partial data example [here](https://htmlpreview.github.io/?https://github.com/abpoll/unsafe/blob/main/examples/phil_frd_partial/notebooks/partial_data_example.html) and full data example [here](https://htmlpreview.github.io/?https://github.com/abpoll/unsafe/blob/main/examples/philadelphia_frd/notebooks/full_data_example.html) to check your results! Note that because `UNSAFE` samples stochastically, your figures and results might look slightly different than the ones here - but they should look similar. 
