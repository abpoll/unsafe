# Examples

This subdirectory hosts two examples of worklows that make use of UNSAFE. The purpose of the `examples/phil_frd_partial` example is to introduce the risk estimation workflow UNSAFE is designed to accommodate and demonstrate that the source code does what we say it does in the technical documentation. This example includes two .zip directories in `phil_frd_partial/data/raw/external/`:

1) `../external/haz/dg_clipped.zip`, and
2) `../external/vuln/ddfs.zip`

Because these two datasets are provided for you, you can run all cells in the `phil_frd_partial/notebooks/partial_data_example.ipynb` notebook. The hazard data in the dg_clipped.zip directory is a clipped depth grid from the full data example included in the `philadelphia_frd/` example. This example includes the depth-damage functions .zip directory, but the hazard data is too large to upload to GitHub. To work through the full data example, you will need to upload the FEMA flood risk database for Philadelphia into `../external/haz/`. You can find this dataset by going go the [FEMA Flood Map Service Center: Search All Products landing page](https://msc.fema.gov/portal/advanceSearch) and searching for Product ID FRD_02040202_PA_GeoTIFFs. Alternatively, you can search under "Jurisdiction" for PENNSYLVANIA -> PHILADELPHIA COUNTY -> PHILADELPHIA COUNTY ALL JURISDICTIONS and then click "Search." As of April of 2024 you will see directories named "Effective Products," "Preliminary Products," "Pending Product," "Historic Products," and "Flood Risk Products." You can click on Flood Risk Products -> Flood Risk Database and then download the GeoTIFFs file. The one used in the full data example was posted on 08/01/2016 and is 2190MB. By the time you are reading this, it's possible the data has been updated, or the website looks different, and we can explore options to use a new FEMA flood risk database product if it's available or check permission with FEMA for us to upload the version we used for our example on a repository like Zenodo.  

You can also test out UNSAFE outside of these examples with your own hazard data in the same county or a different county. To do this, you will need to upload depth-damage functions into the `../data/raw/external/` subdirectory of your project, which you can download from this [Zenodo repository](https://zenodo.org/records/10027236).

## Getting ready to run the examples
To run these examples, you will need to have have [conda](https://docs.conda.io/en/latest/) or [mamba](https://mamba.readthedocs.io/en/latest/) installed. Before you head over to the examples and launch the Jupyter notebooks, you will need to follow these steps:

1) Change your working directory to `examples/` and then run `conda env create -f env/environment.yml` or replace `conda` with `mamba`. 
2) Activate the environment.
3) Create an ipykernel for the environment. If you are new to Jupyter Notebooks and/or conda, please see: https://ipython.readthedocs.io/en/stable/install/kernel_install.html#kernels-for-different-environments. We ran `$ python -m ipykernel install --user --name unsafe`
4) Change your working directory back to the root of the cloned UNSAFE repository and run `pip install -e .` so that the unsafe modules can be imported. 

When you go to the Jupyter notebooks to run the examples, make sure you activate the unsafe environment. 

These instructions were successfully followed, and the examples were successfully re-executed, on the following systems:

1) Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-102-generic x86_64) machine with mamba version 1.4.2
2) macOS Sonoma 14.4.1 (Apple M1 Max, 64GB memory) machine with mamba version 1.5.5