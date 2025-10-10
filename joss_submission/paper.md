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
Flooding is a frequent, widespread, and damaging natural hazard in the United States [@Kousky2020]. Researchers and practitioners increasingly rely on flood-risk estimates to analyze dynamics and inform decisions [@Merz2010; @Trigg2016; @Bates2023; @Mulder2023]. There is increasing demand for flood-risk estimates at the scale of individual assets [@Condon2023]. One driver of this demand is that flood-risk estimates at coarser scales are susceptible to aggregation biases [@Pollack2022; @Condon2023]. Sound flood-risk estimates hinge on careful representation of uncertainties surrounding key inputs driving hazards, exposures, and vulnerabilities at relevant scales [@Bates2023; @Sieg2023; @Saint-Geours2015; @Tate2015; @Rozer2019; @Hosseini-Shakib2024].

Many property-level flood-risk estimation frameworks are silent on the effects of uncertainties  surrounding key inputs [@Schneider2006; @Merz2010; @Saint-Geours2015; @Tate2015; @Sieg2023]. The predominant approach  to estimating economic flood damages in a U.S. setting relies on either the U.S. Army Corps of Engineers (USACE) or Federal Emergency Management Agency (FEMA) depth-damage functions (DDFs) [@Scawthorn2006; @Merz2010; @Tate2015]. In this DDF approach, flood-risk estimates depend on assumptions about several exposure and vulnerability characteristics. Risk estimates are sensitive to the spatial precision of linking a structure to a certain flood depth, the first-floor elevation of a structure, the structure's foundation type, the number of stories of the structure, the main function of the structure (i.e. residential or commercial), and the value of the structure [@Merz2010; @Tate2015; @Wing2020; @Pollack2022; @Xia2024]. Risk estimates are also sensitive to the expected damage for a given depth and the shape of the depth-damage relationship [@Merz2010; @Tate2015; @Rozer2019; @Wing2020]. All of these characteristics are subject to uncertainties which propagate to the resulting risk estimates [@Tate2015; @Saint-Geours2015; @Pollack2022; @Hosseini-Shakib2024].

Here we implemented the Uncertain Structure and Fragility Ensemble (UNSAFE) framework to provide the U.S. flood-risk assessment community with a free and open-source tool for estimating property-level flood risks under uncertainty. UNSAFE represents exposure and vulnerability inputs under uncertainty using entirely free data. This improves on the closest tool we were able to find,[“go-consequences”](https://github.com/USACE/go-consequences) [@USACE-go2024] from the USACE. We could not find documentation, example usage, or an official release for this tool. From our inspection of the GitHub repository, it appears that analysts can use go-consequences to produce stochastic representations of a subset of exposure and vulnerability characteristics in the DDF paradigm. However, this functionality is not available for key drivers like structure value or the functional form of the DDF for a given structure.  

A few other tools are worth mentioning to contextualize the gap `UNSAFE` fills. The most prominent is [Hazus](https://www.fema.gov/flood-maps/products-tools/hazus) [@Scawthorn2006; @Schneider2006; @Tate2015]. Hazus is freely available as a GIS-based desktop application running Windows but cannot be easily modified to accommodate uncertainty in exposure and vulnerability. FEMA also developed the [“Flood Assessment Structure Tool”](https://github.com/nhrap-hazus/FAST?tab=readme-ov-file) [@FEMA2021] to facilitate more efficient deterministic Hazus analyses in Python. This tool appears deprecated. The USACE maintains two published tools for deterministic analyses,([HEC-FIA](https://www.hec.usace.army.mil/confluence/fiadocs/fiaum/latest) [@USACE2021] and [HEC-FDA](https://www.hec.usace.army.mil/software/hec-fda/documentation/CPD-72_V1.4.1.pdf) [@USACE2024]). Lastly, there is the [Delft-FIAT (Fast Impact Assessment Tool)](https://deltares.github.io/Delft-FIAT/stable/) [@Deltares2024], developed and maintained by Deltares. It currently does not accommodate flood risk estimation with uncertainty in exposure and vulnerability inputs, but is open-source and well-documented. Sophisticated users could likely modify the tool to account for uncertainty in inputs; `UNSAFE` streamlines this workflow.

# Summary
`UNSAFE` adopts and expands on a property-level risk assessment framework common in academic research and practice (e.g., [Federal Emergency Management Agency (FEMA) loss avoidance studies](https://www.fema.gov/grants/mitigation/loss-avoidance-studies) [@FEMA2024], [United States Army Corps of Engineers (USACE) feasibility studies](https://www.nad.usace.army.mil/Portals/40/docs/NACCS/10A_PhysicalDepthDmgFxSummary_26Jan2015.pdf) [@USACE2015]). UNSAFE allows users to add parametric uncertainty to the widely used [National Structure Inventory dataset](https://www.hec.usace.army.mil/confluence/nsi/technicalreferences/2019/technical-documentation) [@USACE-nsi2024] (i.e. uncertainty in exposure), and facilitates the use of multiple, potentially conflicting, expert-based DDFs (i.e. deep uncertainty in vulnerability). A tutorial that demonstrates the functionality of `UNSAFE` is available in [this Jupyter notebook](https://github.com/abpoll/unsafe/blob/main/examples/phil_frd_partial/notebooks/partial_data_example.ipynb). The corresponding [GitHub repository](https://github.com/abpoll/unsafe) includes detailed technical documentation on the data sources, distributional assumptions of key parameters, and peer-reviewed methods used in `UNSAFE`.

Figure 1 illustrates how accounting for uncertainty in exposure and vulnerability can result in substantially different estimates of expected flood damages. These results are extracted from [this example Jupyter notebook](https://html-preview.github.io/?url=https://github.com/abpoll/unsafe/blob/main/examples/philadelphia_frd/notebooks/full_data_example.html). Without observations of flooding and resulting damages, we cannot say whether the range of damages produced by `UNSAFE` are well-calibrated. However, this analysis using `UNSAFE` illustrates how implicitly, and incorrectly, assuming that there is no uncertainty in key drivers of flood damages can lead to misleading representations of plausible losses. In fact, the difference between the standard estimate (using HAZUS DDFs without uncertainty) and the expected damage from the ensemble accounting for uncertainty in HAZUS DDFs appears to increase as the number of houses in the case study increases. Note that in cases where observations of flooding and resulting damages are available, `UNSAFE` can serve as a framework to calibrate parameters and system relationships.


![**Demonstration of the UNSAFE approach.** Accounting for uncertainty in exposure and vulnerability can result in a large range of plausible flood damage estimates and increases the expected value of risk. The red vertical line shows the expected annual damage estimate produced from the standard HAZUS approach, which neglects uncertainty in depth-damage functions and national structure inventory records. The orange histogram shows the range of plausible damage estimates when accounting for uncertainty in HAZUS depth-damage functions and national structure inventory records. The blue histogram shows the same, but with uncertainty in NACCS depth-damage functions instead of HAZUS ones. At the top, orange and blue boxplots summarize the distributions of HAZUS and NACCS losses, respectively. The red diamond denotes the ensemble mean for each distribution. \label{fig:philly_results}](philly_results.png)

# Acknowledgements
This research was supported by the U.S. Department of Energy, Office of Science, as part of research in MultiSector Dynamics, Earth and Environmental System Modeling Program and Dartmouth College. All errors and opinions are those of the authors and not of the supporting entities.

Software License: `UNSAFE` is distributed under the BSD-2-Clause license. The authors do not assume responsibility for any (mis)use of the provided code.

# References