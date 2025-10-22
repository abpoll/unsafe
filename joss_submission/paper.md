---
title: 'UNSAFE: An UNcertain Structure And Fragility Ensemble framework for property-level flood risk estimation'
tags:
  - flood risk
  - uncertainty
  - climate impacts
  - natural disasters
  - Python
authors:
  - name: Adam Pollack
    corresponding: true
    email: adam.b.pollack@dartmouth.edu
    orcid: 0000-0001-6642-0591
    affiliation: "1, 2"
  - name: James Doss-Gollin
    orcid: 0000-0002-3428-2224
    affiliation: 3
  - name: Vivek Srikrishnan
    orcid: 0000-0003-0049-3805
    affiliation: 4
  - name: Klaus Keller
    orcid: 0000-0002-5451-8687
    affiliation: 1
affiliations:
 - name: Thayer School of Engineering, Dartmouth College, USA
   index: 1
 - name: School of Earth, Environment, and Sustainability, University of Iowa, USA
   index: 2
 - name: Department of Civil and Environmental Engineering, Rice University, USA
   index: 3
 - name: Department of Biological and Environmental Engineering, Cornell University, USA
   index: 4
date: 22 September 2025
bibliography: paper.bib

---
# Statement of Need
Flooding is among the most frequent and damaging hazards in the United States [@Kousky2020]. Researchers and practitioners increasingly use flood-risk estimates to analyze dynamics and inform decisions [@Merz2010; @Trigg2016; @Bates2023; @Mulder2023]. There is increasing demand for flood-risk estimates at the scale of individual assets [@Condon2023]. One driver of this demand is that flood-risk estimates at coarser scales are susceptible to aggregation biases [@Pollack2022; @Condon2023]. Robust flood-risk estimates require explicit representation of uncertainties surrounding key inputs driving hazards, exposures, and vulnerabilities at relevant scales [@Bates2023; @Sieg2023; @Saint-Geours2015; @Tate2015; @Rozer2019; @Hosseini-Shakib2024].

Many property-level flood-risk estimation frameworks are silent on the effects of uncertainties surrounding key inputs [@Schneider2006; @Merz2010; @Saint-Geours2015; @Tate2015; @Sieg2023]. The predominant approach  to estimating economic flood damages in a U.S. setting relies on either the U.S. Army Corps of Engineers (USACE) or Federal Emergency Management Agency (FEMA) depth-damage functions (DDFs) [@Scawthorn2006; @Merz2010; @Tate2015]. In this DDF approach, flood-risk estimates depend on assumptions about several exposure and vulnerability characteristics. Risk estimates are sensitive to the spatial precision of linking a structure to a certain flood depth, the first-floor elevation of a structure, the structure's foundation type, the number of stories of the structure, the main function of the structure (i.e. residential or commercial), and the value of the structure [@Merz2010; @Tate2015; @Wing2020; @Pollack2022; @Xia2024]. Risk estimates are also sensitive to the expected damage for a given depth and the shape of the depth-damage relationship [@Merz2010; @Tate2015; @Rozer2019; @Wing2020]. All of these characteristics are subject to uncertainties which propagate to the resulting risk estimates [@Tate2015; @Saint-Geours2015; @Pollack2022; @Hosseini-Shakib2024].

Here we implemented the Uncertain Structure and Fragility Ensemble (UNSAFE) framework to provide the U.S. flood-risk assessment community with a free and open-source tool for estimating property-level flood risks under uncertainty. UNSAFE represents exposure and vulnerability inputs under uncertainty using entirely free data. This extends key functionalities of the most comparable publicly available tool, [“go-consequences”](https://github.com/USACE/go-consequences) [@USACE-go2024], developed by the USACE, for which limited documentation and usage examples are available. Examination of the repository suggests that go-consequences can produce stochastic representations of selected exposure and vulnerability characteristics in the DDF paradigm. However, this functionality is not available for key drivers like structure value or the functional form of the DDF for a given structure.  

Several existing tools help contextualize the methodological gap that UNSAFE addresses. The most prominent is [Hazus](https://www.fema.gov/flood-maps/products-tools/hazus) [@Scawthorn2006; @Schneider2006; @Tate2015], a freely available GIS-based desktop application for Windows that supports deterministic flood-damage assessments but cannot be readily modified to incorporate uncertainty in exposure and vulnerability. FEMA also developed the [“Flood Assessment Structure Tool”](https://github.com/nhrap-hazus/FAST?tab=readme-ov-file) [@FEMA2021] to facilitate more efficient deterministic Hazus analyses in Python, although this tool appears to be deprecated. The USACE maintains two published tools for deterministic analyses,([HEC-FIA](https://www.hec.usace.army.mil/confluence/fiadocs/fiaum/latest) [@USACE2021] and [HEC-FDA](https://www.hec.usace.army.mil/software/hec-fda/documentation/CPD-72_V1.4.1.pdf) [@USACE2024]). Lastly, there is the [Delft-FIAT (Fast Impact Assessment Tool)](https://deltares.github.io/Delft-FIAT/stable/) [@Deltares2024], developed and maintained by Deltares. It currently does not accommodate flood risk estimation with uncertainty in exposure and vulnerability inputs, but is open-source and well-documented. Advanced users could, in principle, extend its functionality to represent such uncertainty. `UNSAFE` provides a direct and streamlined framework for doing so.

# Summary
`UNSAFE` adopts and expands on a property-level risk assessment framework common in academic research and practice (e.g., [Federal Emergency Management Agency (FEMA) loss avoidance studies](https://www.fema.gov/grants/mitigation/loss-avoidance-studies) [@FEMA2024], [United States Army Corps of Engineers (USACE) feasibility studies](https://www.nad.usace.army.mil/Portals/40/docs/NACCS/10A_PhysicalDepthDmgFxSummary_26Jan2015.pdf) [@USACE2015]). UNSAFE allows users to add parametric uncertainty to building inventories, such as the widely used [National Structure Inventory (NSI) dataset](https://www.hec.usace.army.mil/confluence/nsi/technicalreferences/2019/technical-documentation) [@USACE-nsi2024] (i.e. uncertainty in exposure), and facilitates the use of multiple, potentially conflicting, expert-based DDFs (i.e. deep uncertainty in vulnerability). As of now, `UNSAFE` includes functionality to conduct risk assessments on residential properties of at most 3 stories given limitations in representing uncertainty in depth-damage relationships for other structures. This subset of structures represents a large proportion of structures exposed to flooding, and is a common inventory focus in research [@Pollack2025-nsi]. 

## Target audience and use cases
`UNSAFE` is designed for a technical user base. Analysts in research, government, or industry that manage custom code to conduct flood-risk assessments may benefit from integrating `UNSAFE`'s functionality into their workflows. Maintainers of other flood-risk estimation software are also welcome to adapt `UNSAFE`'s methods for estimating damage under uncertainty and integrate it into their tools. `UNSAFE` could also serve as the back-end risk estimation software for user-interfaces and tools that aim to bridge the gap between non-technical users and robust flood-risk estimates. 

To date, several peer-reviewed studies use `UNSAFE` for automating flood-risk estimation under uncertainty based on the widely used NSI [@USACE-nsi2024] (e.g., [@Pollack2025-j40] and [@Bhaduri2025]). A recently published preprint uses `UNSAFE` with a local, more accurate building inventory and compares the obtained risk estimates to those obtained with the NSI [@Pollack2025-nsi]. 


## Technical details
The corresponding [GitHub repository](https://github.com/abpoll/unsafe) includes detailed technical documentation on the data sources, distributional assumptions of key parameters, and peer-reviewed methods used in `UNSAFE`. 

Users must supply flood depth data for their analyses. This data may be at any spatial resolution. Users can link flood depths to structures via the `pnt_sample_depths()` or `get_inundations()` functions in the `unsafe.exp` module. 

For analyses using the NSI as the base structure inventory, users can specify the U.S. county FIPS code for their study domain and run `download_raw()` from the `unsafe.download` module. For analyses not using the NSI, analysts must add their inventory to their data directory and manage filepaths accordingly. 

To estimate flood risk, it is sufficient for analysts to supply flood depth data and specify a base structure inventory. The main functionality of of `UNSAFE` is executed in the following function in the `unsafe.ensemble` module:

```
def get_loss_ensemble(
    structures_df,
    depths_df,
    config=None,
    vuln_dir=None,
    random_seed=None
):
    
    """
    Generate an ensemble of structure realizations with uncertainty and calculate damages.
    
    This function creates multiple realizations of structures by introducing
    uncertainty in selected characteristics and calculating damages.
    
    Parameters
    ----------
    structures_df : pandas.DataFrame or geopandas.GeoDataFrame
        DataFrame containing all structures with their characteristics.
        Must have a unique identifier column (specified in config['id_col']).
    
    depths_df : pandas.DataFrame
        DataFrame containing depth values for structures.
        Index or id_column should match structures_df's id_column.
        Only structures with non-zero depths will be used for ensemble generation.
    
    vuln_dir : str or Path
        Path to directory containing processed DDF files.
    
    config : dict, optional
        Configuration dictionary with the following keys:
        - 'n_sow': Number of ensemble members (default: 1000)
        - 'struct_list': List of characteristics to vary (e.g., ['ffe', 'val_struct'])
        - 'ffe_dict': Dict mapping foundation types to FFE distribution parameters
        - 'coef_var': Float for structure value uncertainty (default: 0.2)
        - 'ref_col': Column name for spatial reference (default: 'tract_id')
        - 'id_col': Column name for structure identifier (default: 'fd_id')
        - 'ddfs': List of depth-damage function types to use (e.g., ['hazus', 'naccs'])
        - 'base_adj': Boolean for starting basement flooding from bottom of basement
        - 'found_param': Prop. of structures in each ref_id area with various foundation types
        - 'stories_param': Prop. of structures in each ref_id area with various stories
        - 'depth_min': float for filtering low depths (in m) from damage estimation (default: 0)
    
    random_seed : int, optional
        Random seed for reproducibility.
    
    Returns
    -------
    pandas.DataFrame
        DataFrame containing the ensemble with n_sow realizations of each structure.
        Includes columns for each uncertain characteristic and damage estimates.
    
    Notes
    -----
    The function follows this workflow:
    1. Generate reference distributions from the full structures dataset
    2. Filter structures to those with non-zero depths (if depths_df provided)
    3. Generate ensemble members for the filtered structures
    4. Calculate damages using the specified DDFs
    """
```

This function returns a DataFrame containing an ensemble of damage estimates and realizations of uncertain characteristics n_sow realizations for a sample size of *n_sow*. After running this function, a user can conduct a wide range of analyses (e.g., as done in [@Bhaduri2025 or @Pollack2025-nsi]) though it is also possible to use `UNSAFE` to obtain more robust estimates of the mean damage estimate for a structure across the sampled realizations (e.g., [@Pollack2025-j40])

The function includes default values for the options in the `config` dict argument. The default behavior for the function infers the uncertain distribution for parameters such as a structure's number of stories or foundation type based on overall census tract proportions. Users may modify these priors with the keys `stories_param` or `found_param`. Users may modify other priors as well. For example, users can update uncertainty around structure value assessment by modifying the `coef_var` key, or first-floor elevation with structure-level updates or a dict that maps foundation types to a distribution of possible foundation heights. 

Users may elect not to account for uncertainty in certain exposure characteristics by removing these features from the list passed to the `struct_list` key in the `config` dict, but the function always accounts for depth-damage function uncertainty. The `ensemble.py` module includes functions for neglecting uncertainty in depth-damage functions in order for analysts to implement the most common approach in research and practice, if desired.

Users may also add additional data sources to a configuration file (e.g., flood risk analyses often use spatial data on administrative zones or socioeconomic data) and `download_raw()` will download the corresponding data and place it in the specified subdirectories. The recommended configuration file structure is described in detail in the file `examples/phil_frd_partial/notebooks/partial_data_example.ipynb` available at the software's [Zenodo repository](https://zenodo.org/records/17362970). 

Before generating an ensemble, there are several processing steps `UNSAFE` does not automate to allow for greater analyst flexibility. These steps are best illustrated through an example. 

## Example
A tutorial that demonstrates the basic functionality of `UNSAFE` is available in the file `examples/phil_frd_partial/notebooks/partial_data_example.ipynb` available at the software's [Zenodo repository](https://zenodo.org/records/17362970). 

In this example, we conduct a very small case study on a small area in Philadelphia based on depth grids available via FEMA's risk map project. The notebook serves to demonstrate the following workflow to help introduce new users to the `UNSAFE` framework, and to allow them to test that the code does what it says it does. 

1) Configure the working directory structure and workflow parameters;
2) Download and unzip data;
3) Subset the full structure inventory to single-family structures and convert the data to a GeoDataFrame;
4) Specify a spatial extent of your study area (i.e. county shapefile or a study boundary) and process reference files through clipping (e.g. census tract data);
5) Process expert DDFs for use in ensembles;
6) Process social vulnerability data by linking it with corresponding reference data (e.g. linking Climate and Economic Justice Screening Tool with census tracts);
7) Prepare the National Flood Hazard Layer data for identifying structure location in and outside of the federal floodplain;
8) Link structures to all vector spatial data;
9) Link structures to inundation data, provided as raster(s);
10) Prepare the structure inventory for loss estimation (this base inventory can be used for estimating losses without uncertainty);
11) Generate an ensemble of plausible structure realizations based on several parameters users can specify;
12) Estimate expected annual losses for each ensemble member for a set of design events. Each ensemble member has a unique draw from the DDF distribution. Users can also estimate expected annual losses without uncertainty in exposure and vulnerability. 

We also provide code for producing some visualizations. 

Figure 1 illustrates how accounting for uncertainty in exposure and vulnerability can result in substantially different estimates of expected flood damages. These results are extracted from [this example Jupyter notebook](https://html-preview.github.io/?url=https://github.com/abpoll/unsafe/blob/main/examples/philadelphia_frd/notebooks/full_data_example.html). Without observations of flooding and resulting damages, we cannot say whether the range of damages produced by `UNSAFE` are well-calibrated. However, this analysis using `UNSAFE` illustrates how implicitly, and incorrectly, assuming that there is no uncertainty in key drivers of flood damages can lead to misleading representations of plausible losses. In fact, the difference between the standard estimate (using HAZUS DDFs without uncertainty) and the expected damage from the ensemble accounting for uncertainty in HAZUS DDFs appears to increase as the number of houses in the case study increases. Note that in cases where observations of flooding and resulting damages are available, `UNSAFE` can serve as a framework to calibrate parameters and system relationships.

![**Demonstration of the UNSAFE approach.** Accounting for uncertainty in exposure and vulnerability can result in a large range of plausible flood damage estimates and increases the expected value of risk. The red vertical line shows the expected annual damage estimate produced from the standard HAZUS approach, which neglects uncertainty in depth-damage functions and national structure inventory records. The orange histogram shows the range of plausible damage estimates when accounting for uncertainty in HAZUS depth-damage functions and national structure inventory records. The blue histogram shows the same, but with uncertainty in NACCS depth-damage functions instead of HAZUS ones. At the top, orange and blue boxplots summarize the distributions of HAZUS and NACCS losses, respectively. The red diamond denotes the ensemble mean for each distribution. \label{fig:philly_results}](philly_results.png)


## Limitations
While `UNSAFE` improves analysts' ability to account for often overlooked uncertainties in flood-risk estimation, it misses several desired features that we are actively working on. 

For example, as mentioned earlier, `UNSAFE` only includes functionality to conduct risk assessments on residential properties of at most 3 stories given limitations in representing uncertainty in depth-damage relationships for other structures. We aim to make `UNSAFE` operational for all structure types. 

In addition, `UNSAFE`'s current functionality is strongly conditioned to the common depth-damage function paradigm for flood-risk estimation in the U.S. There are many structural characteristics and broader hazard-damage relationships that may be desirable for some analysts. We aim to expand `UNSAFE`'s capabilities beyond the depth-damage function paradigm for more generic application. 

Finally, `UNSAFE` may be difficult to use for calibrating the distributions of uncertain inputs. This is an important gap we aim to reconcile. 


# Acknowledgements
This research was supported by the U.S. Department of Energy, Office of Science, as part of research in MultiSector Dynamics, Earth and Environmental System Modeling Program and Dartmouth College. All errors and opinions are those of the authors and not of the supporting entities.

Software License: `UNSAFE` is distributed under the BSD-2-Clause license. The authors do not assume responsibility for any (mis)use of the provided code.

# References
