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
    orcid: 0000-0002-7304-3883
    affiliation: 1
  - name: James Doss-Gollin
    orcid: 0000-0002-3428-2224
    affiliation: 2
  - name: Vivek Srikrishnan
    orcid: 0000-0003-0049-3805
    affiliation: 3
  - name: Klaus Keller
    orcid: 0000-0002-5451-8687
    affiliation: 1
affiliations:
 - name: Thayer School of Engineering, Dartmouth College, USA
   index: 1
 - name: Department of Civil and Environmental Engineering, Rice University, USA
   index: 2
 - name: Department of Biological and Environmental Engineering, Cornell University, USA
   index: 3
date: 2 April 2024
bibliography: paper.bib

---
# Statement of Need
Flooding is a frequent, widespread, and damaging natural hazard in the United States [@Kousky2020]. Economic flood risk estimates are increasingly used in research and practice to help inform management practices and policies [@Merz2010; @Trigg2016; @Bates2023; @Mulder2023]. There is increasing demand for flood risk estimates at the scale of individual assets[@Condon2023]. This is due to the large number of decisions that can be informed by these estimates, such as insurance premium rates and risk reduction interventions to houses. In addition, flood risk estimates at coarser scales are subject to aggregation bias if the tails of the distributions of key drivers are not represented [@Pollack2022]. It is easiest to capture these parts of the distributions by estimating flood risk at the property level and then aggregating risk estimates. However, due to measurement and modeling error of hazard, exposure, and vulnerability when observations are available at the scale of individual assets, it is crucial that flood risk estimates account for uncertainty in key inputs [@Bates2023; @Sieg2023].

It is common for property-level economic flood risk assessments to overlook uncertainty in key inputs [@Tate2015]. When uncertainty is incorporated into these assessments, it is more common to account for uncertainty in flood hazard than in exposure or vulnerability [@Hosseini-Shakib2024]. While it is a common finding that flood risk estimates are most sensitive to uncertainty in flood hazard estimates, overlooking uncertainty in exposure and vulnerability can bias risk estimates [De_Moel@2011; De_Moel@2014; @Saint-Geours2015; @Tate2015; @Rozer2019; @Hosseini-Shakib2024].

The predominant method to estimate economic flood damages in a U.S. setting is with U.S. Army Corps of Engineers (USACE) or Federal Emergency Management Agency (FEMA) depth-damage functions (DDFs) [@Merz2010; @Tate2015]. In this DDF paradigm,  flood-risk estimates are sensitive to several exposure and vulnerability characteristics. In terms of exposure, risk estimates are sensitive to the spatial precision of linking a structure to a certain flood depth, the first-floor elevation of a structure, the structure's foundation type, the number of stories of the structure, the main function of the structure (i.e. residential or commercial), and the value of the structure [@Merz2010; @Tate2015; @Wing; 2020; @Pollack2022; @Xia2024]. In terms of vulnerability, risk estimates are sensitive to the expected damage for a given depth and the shape of the depth-damage relationship [@Merz2010; @Tate2015; @Rozer2019; @Wing; 2020].

To meet the need for a free and open-source tool for representing exposure and vulnerability under uncertainty for property-level flood-risk estimation in the U.S., we created The Uncertain Structure and Fragility Ensemble (UNSAFE) framework. As far as we can tell, this is the first such tool that fills this need. The closest tool we can find, the [“go-consequences” tool](https://github.com/USACE/go-consequences) is developed by the USACE. It appears that analysts can use go-consequences to produce stochastic representations of a subset of exposure and vulnerability characteristics in the DDF paradigm. However, it does not appear that analysts can produce stochastic representations for key drivers like structure value or the functional form of the DDF for a given structure. In terms of usability, the repository does not have documentation, example usage, or an official release.

A few other tools are worth mentioning to contextualize the gap UNSAFE fills. The most prominent too., [Hazus](https://www.fema.gov/flood-maps/products-tools/hazus), is free and widely used, but is provided as a GIS-based desktop application for Windows and cannot be easily modified to accommodate uncertainty in exposure and vulnerability. FEMA also developed the [“Flood Assessment Structure Tool”](https://github.com/nhrap-hazus/FAST?tab=readme-ov-file) to facilitate more efficient Hazus analyses in Python. This was designed for deterministic analyses and appears deprecated. The USACE maintains two published tools,([HEC-FIA](https://www.hec.usace.army.mil/confluence/fiadocs/fiaum/latest) and [HEC-FDA](https://www.hec.usace.army.mil/software/hec-fda/documentation/CPD-72_V1.4.1.pdf)), which appear primarily designed for internal users since the documentations state that technical support cannot be provided for non-Corps users and the software must be used as-is. Another tool worth mentioning is the [Delft-FIAT (Fast Impact Assessment Tool)](https://deltares.github.io/Delft-FIAT/stable/), developed and maintained by Deltares. It currently does not accommodate flood risk estimation with uncertainty in exposure and vulnerability inputs, but is open-source and well-documented. Sophisticated users could likely modify the tool to account for uncertainty in inputs; UNSAFE streamlines this workflow.

# Summary
UNSAFE modifies a property-level risk assessment framework common in academic research and practice (e.g., [Federal Emergency Management Agency (FEMA) loss avoidance studies](https://www.fema.gov/grants/mitigation/loss-avoidance-studies), [United States Army Corps of Engineers (USACE) feasibility studies](https://www.nad.usace.army.mil/Portals/40/docs/NACCS/10A_PhysicalDepthDmgFxSummary_26Jan2015.pdf)). At a high-level, UNSAFE allows users to add parametric uncertainty to the widely used [National Structure Inventory dataset](https://www.hec.usace.army.mil/confluence/nsi/technicalreferences/2019/technical-documentation) (i.e. uncertainty in exposure), and facilitates the use of multiple, potentially conflicting, expert-based DDFs (i.e. deep uncertainty in vulnerability). The expected use case for UNSAFE is demonstrated in the `examples/philadelphia_frd/notebooks/partial_data_example.ipynb` notebook. 

Figure 1 illustrates how accounting for uncertainty in exposure and vulnerability can result in a substantially different representation of expected flood damages. These results are extracted from the full example in the `examples/philadelphia_frd/notebooks/partial_data_example.ipynb` notebook. Without observations of flooding and resulting damages, we cannot say whether the range of damages produced by UNSAFE are well-calibrated. However, we can recognize that implicitly, and incorrectly, assuming that there is no uncertainty in key drivers of flood damages leads to a misleading representation of plausible losses. In fact, the difference between the standard estimate (using HAZUS DDFs without uncertainty) and the expected damage from the ensemble accounting for uncertainty in HAZUS DDFs appears to increase as the number of houses in the case study increases. We also note that in cases where observations of flooding and resulting damages are available, UNSAFE can be used to identify which combinations of parameters and system relationships lead to well-calibrated damage estimates. 

![Accounting for uncertainty in exposure and vulnerability results in a large range of plausible flood damage estimates. The red vertical line shows the expected annual damage estimate produced from the standard HAZUS approach, which accounts for no uncertainty in depth-damage functions or national structure inventory records. The orange histogram shows the range of plausible damage estimates when accounting for uncertainty in HAZUS depth-damage functions and national structure inventory records. The blue histogram shows the same, but with uncertainty in NACCS depth-damage functions instead of HAZUS ones. \label{fig:philly_results}](philly_results_temp.png)

# References