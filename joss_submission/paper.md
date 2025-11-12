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
Flooding is among the most frequent and damaging hazards in the United States [@Kousky2020]. Researchers and practitioners increasingly use flood-risk estimates to analyze dynamics and inform decisions [@Merz2010; @Trigg2016; @Bates2023; @Mulder2023]. As such, there is increasing demand for flood-risk estimates at the scale of individual assets [@Condon2023]. One driver of this demand is that flood-risk estimates at coarser scales are susceptible to aggregation biases [@Pollack2022; @Condon2023]. Crucially, robust flood-risk estimates at any scale require explicit representation of uncertainties surrounding key inputs driving hazards, exposures, and vulnerabilities [@Bates2023; @Sieg2023; @Saint-Geours2015; @Tate2015; @Rozer2019; @Hosseini-Shakib2024].

Many property-level flood-risk estimation frameworks are silent on the effects of uncertainties surrounding key inputs [@Schneider2006; @Merz2010; @Saint-Geours2015; @Tate2015; @Sieg2023]. The predominant approach  to estimating economic flood damages in a U.S. setting relies on depth-damage functions (DDFs), typically developed by the U.S. Army Corps of Engineers (USACE) or Federal Emergency Management Agency (FEMA) [@Scawthorn2006; @Merz2010; @Tate2015]. In this DDF approach, flood-risk estimates depend on assumptions about several exposure and vulnerability characteristics. Risk estimates are sensitive to the spatial precision of linking a structure to a certain flood depth, the first-floor elevation of a structure, the structure's foundation type, the number of stories of the structure, the main function of the structure (i.e., residential or commercial), and the value of the structure [@Merz2010; @Tate2015; @Wing2020; @Pollack2022; @Xia2024]. Risk estimates are also sensitive to the expected damage for a given depth and the shape of the depth-damage relationship [@Merz2010; @Tate2015; @Rozer2019; @Wing2020]. All of these characteristics are subject to uncertainties that propagate to the resulting risk estimates [@Tate2015; @Saint-Geours2015; @Pollack2022; @Hosseini-Shakib2024].

Here, we implemented the Uncertain Structure and Fragility Ensemble (UNSAFE) framework to provide the U.S. flood-risk assessment community with a free and open-source tool for estimating property-level flood risks under uncertainty. UNSAFE represents exposure and vulnerability inputs under uncertainty using entirely free data. This extends key functionalities of the most comparable publicly available tool, [“go-consequences”](https://github.com/USACE/go-consequences) [@USACE-go2024], developed by the USACE, for which limited documentation and usage examples are available. Examination of the repository suggests that go-consequences can produce stochastic representations of selected exposure and vulnerability characteristics in the DDF paradigm. However, this functionality is not available for key drivers like structure value or the functional form of the DDF for a given structure.  

Several existing tools help contextualize the methodological gap that UNSAFE addresses. The most prominent is [Hazus](https://www.fema.gov/flood-maps/products-tools/hazus) [@Scawthorn2006; @Schneider2006; @Tate2015], a freely available GIS-based desktop application for Windows that supports deterministic flood-damage assessments but cannot be readily modified to incorporate uncertainty in exposure and vulnerability. FEMA also developed the [“Flood Assessment Structure Tool”](https://github.com/nhrap-hazus/FAST?tab=readme-ov-file) [@FEMA2021] to facilitate more efficient deterministic Hazus analyses in Python, although this tool appears to be deprecated. The USACE maintains two published tools for deterministic analyses,([HEC-FIA](https://www.hec.usace.army.mil/confluence/fiadocs/fiaum/latest) [@USACE2021] and [HEC-FDA](https://www.hec.usace.army.mil/software/hec-fda/documentation/CPD-72_V1.4.1.pdf) [@USACE2024]). Lastly, there is the [Delft-FIAT (Fast Impact Assessment Tool)](https://deltares.github.io/Delft-FIAT/stable/) [@Deltares2024], developed and maintained by Deltares. It currently does not accommodate flood risk estimation with uncertainty in exposure and vulnerability inputs, but is open-source and well-documented. Advanced users could, in principle, extend its functionality to represent such uncertainty. `UNSAFE` provides a direct and streamlined framework for doing so.

# Summary
`UNSAFE` adopts and expands on a property-level risk assessment framework common in academic research and practice (e.g., [Federal Emergency Management Agency (FEMA) loss avoidance studies](https://www.fema.gov/grants/mitigation/loss-avoidance-studies) [@FEMA2024], [United States Army Corps of Engineers (USACE) feasibility studies](https://www.nad.usace.army.mil/Portals/40/docs/NACCS/10A_PhysicalDepthDmgFxSummary_26Jan2015.pdf) [@USACE2015]). UNSAFE allows users to add parametric uncertainty to building inventories, such as the widely used [National Structure Inventory (NSI) dataset](https://www.hec.usace.army.mil/confluence/nsi/technicalreferences/2019/technical-documentation) [@USACE-nsi2024] (i.e., uncertainty in exposure), and facilitates the use of multiple, potentially conflicting, expert-based DDFs (i.e., deep uncertainty in vulnerability). In its current implementation, `UNSAFE` supports risk assessments for residential properties up to three stories, due to limitations in representing uncertainty in depth-damage relationships for other structures. This subset of structures represents a large proportion of structures exposed to flooding, and is a common inventory focus in research [@Pollack2025-nsi]. 

## Target audience and use cases
`UNSAFE` is designed for a technical user base. Analysts in research, government, or industry who manage custom code to conduct flood-risk assessments may benefit from integrating `UNSAFE`'s functionality into their workflows. Maintainers of other flood-risk estimation software are also welcome to adapt `UNSAFE`'s methods for estimating damage under uncertainty and integrate it into their tools. `UNSAFE` could also serve as the back-end risk estimation software for user interfaces and tools that aim to bridge the gap between non-technical users and robust flood-risk estimates. 

To date, several peer-reviewed studies use `UNSAFE` for automating flood-risk estimation under uncertainty based on the widely used NSI [@USACE-nsi2024] (e.g., @Pollack2025-j40 and @Bhaduri2025). A recently published preprint uses `UNSAFE` with a local, more accurate building inventory and compares the obtained risk estimates to those obtained with the NSI [@Pollack2025-nsi]. 


## Technical details

The corresponding [GitHub repository](https://github.com/abpoll/unsafe) includes detailed documentation on data sources, distributional assumptions of key parameters, and the peer-reviewed methods implemented in the `UNSAFE` package.

Users provide flood depth data at any spatial resolution and link these data to building or infrastructure inventories within their study area. For studies based on the National Structure Inventory (NSI), `UNSAFE` can automatically retrieve the relevant structural data using the county FIPS code. Analysts using other inventories can include their own datasets within the project directory.

Once the structural and flood depth data are prepared, `UNSAFE` estimates flood risk by combining these inputs through its ensemble modeling framework, which generates multiple realizations of uncertain structural and environmental characteristics to produce a comprehensive set of flood damage estimates. This ensemble allows users to quantify uncertainty and conduct a wide range of risk analyses, as demonstrated in previous applications (e.g., @Bhaduri2025; @Pollack2025-nsi). The software can also be used to produce more robust mean damage estimates across sampled realizations (@Pollack2025-j40).

By default, `UNSAFE` assigns probability distributions to key structural attributes such as the number of stories, foundation type, and replacement value, based on local census tract statistics. Users can adjust these assumptions by providing alternative priors that better reflect their study area or data quality. The framework also allows analysts to represent or suppress uncertainty in specific exposure characteristics, while always maintaining uncertainty in depth–damage relationships, which is a critical component of risk estimation.

Additional contextual data, including administrative boundaries and socioeconomic indicators, can be incorporated through external configuration files. `UNSAFE` automatically retrieves these data and organizes them within the appropriate project directories. Before generating an ensemble, there are several processing steps `UNSAFE` does not automate to allow for greater analyst flexibility, such as processing external building inventories and flood hazard data. These steps are best illustrated through an example. 

## Example
A tutorial that demonstrates the core functionality of `UNSAFE` is available in the notebook `examples/phil_frd_partial/notebooks/partial_data_example.ipynb` available at the software's [Zenodo repository](https://zenodo.org/records/17362970). The tutorial presents a small case study for an area in Philadelphia using depth grids from FEMA’s Risk MAP project. It guides users through the full analysis workflow helping new users verify that the software performs as expected.

The example covers essential preprocessing and analysis steps, including preparing the project directory, retrieving and organizing input data, subsetting building inventories, defining the study extent, linking structures to flood hazard data, and generating ensembles of plausible structural realizations. The notebook also demonstrates how to estimate expected annual losses for different design events and visualize the resulting uncertainty in flood damage outcomes. We also provide code for producing a range of visualizations. 

Figure 1 illustrates how accounting for uncertainty in exposure and vulnerability can result in substantially different estimates of expected flood damages. Without observations of flooding and resulting damages (which is very common in flood-risk assessment), we cannot say whether the range of damages produced by `UNSAFE` is well-calibrated. However, this analysis using `UNSAFE` illustrates how implicitly, and incorrectly, assuming that there is no uncertainty in key drivers of flood damages can lead to misleading representations of plausible losses. In fact, the difference between the standard estimate (using HAZUS DDFs without uncertainty) and the expected damage from the ensemble accounting for uncertainty in HAZUS DDFs appears to increase as the number of houses in the case study increases. Note that in cases where observations of flooding and resulting damages are available, `UNSAFE` can serve as a framework to calibrate parameters and system relationships.

![**Demonstration of the UNSAFE approach.** Accounting for uncertainty in exposure and vulnerability can result in a large range of plausible flood damage estimates and increases the expected value of risk. The red vertical line shows the expected annual damage estimate produced from the standard HAZUS approach, which neglects uncertainty in depth-damage functions and national structure inventory records. The orange histogram shows the range of plausible damage estimates when accounting for uncertainty in HAZUS depth-damage functions and national structure inventory records. The blue histogram shows the same, but with uncertainty in NACCS depth-damage functions instead of HAZUS ones. At the top, orange and blue boxplots summarize the distributions of HAZUS and NACCS losses, respectively. The red diamond denotes the ensemble mean for each distribution. \label{fig:philly_results}](philly_results.png)


## Limitations
While `UNSAFE` helps analysts to better account for often overlooked uncertainties in flood-risk estimation, the current version misses several desired features. For example, as mentioned above, `UNSAFE` is designed for risk assessments on residential properties of at most three stories. This is due to limitations in representing uncertainty in depth-damage relationships for other structures. We aim to make `UNSAFE` operational for more structure types. 

In addition, `UNSAFE`'s current functionality is strongly conditioned to the common depth-damage function paradigm for flood-risk estimation in the United States. There are many structural characteristics and broader hazard-damage relationships that may be desirable for some analysts. We aim to expand `UNSAFE`'s capabilities beyond the depth-damage function paradigm for a more generic application. 

Further, `UNSAFE` has limited functionality regarding the wide range of possible uncertainty analyses. For example, `UNSAFE` only accommodates random sampling based on parametric uncertainty and what-if-based exploration of structural uncertainties. There are many uncertainty analyses that require other sampling techniques or additional modules for calibrating prior distributions. 

Finally, we recommend that analysts perform their own convergence analysis to ensure they sufficiently sample from the input uncertainties under consideration. A recent preprint finds that 500 samples (*i.e.,* setting `n_sow=500`) is sufficient for converged mean property-level flood-risk estimates [@Pollack2025-nsi]. Still, analysts pursuing different outcomes of interest may need fewer or more samples. 


# Acknowledgements
This research was supported by the U.S. Department of Energy, Office of Science, as part of research in MultiSector Dynamics, Earth and Environmental System Modeling Program and Dartmouth College. All errors and opinions are those of the authors and not of the supporting entities.

Software License: `UNSAFE` is distributed under the BSD-2-Clause license. The authors do not assume responsibility for any (mis)use of the provided code.

# References
