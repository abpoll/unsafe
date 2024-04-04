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

# Statement of need
Flooding is a frequent, widespread, and damaging natural hazard in the United States [@Kousky2020]. Economic flood risk estimates are increasingly used in research and practice to help inform management practices and policies [@Merz2010; @Trigg2016; @Bates2023; @Mulder2023]. Economic flood risk is estimated as a function of hazard (i.e. the features of a flood over space and time), exposure (i.e. the assets that experience inundation from a flood), and vulnerability (i.e. the susceptibility of exposed assets to damage for a set of flood features) [@Merz2010].

There is increasing demand for flood risk estimates at the scale of individual assets[@Condon2023]. This is due to the large number of decisions that can be informed by these estimates, such as insurance premium rates and risk reduction interventions to houses. In addition, flood risk estimates at coarser scales are subject to aggregation bias if the tails of the distributions of key drivers are not represented [@Pollack2022]. It is easiest to capture these parts of the distributions by estimating flood risk at the property level and then aggregating risk estimates. However, due to limitations in observing drivers of flood risk at this scale, and measurement and modeling error of hazard, exposure, and vulnerability when observations are available at the scale of individual assets, it is crucial that flood risk estimates account for uncertainty in key inputs [@Bates2023; @Sieg2023].

It is common for property-level economic flood risk assessments to overlook uncertainty in all inputs [@Tate2015]. When uncertainty is incorporated into these assessments, it is more common to account for uncertainty in flood hazard than in exposure or vulnerability [@Hosseini-Shakib2024]. While it is a common finding that flood risk estimates are most sensitive to uncertainty in flood hazard estimates, overlooking uncertainty in exposure and vulnerability can bias risk estimates [De_Moel@2011; De_Moel@2014; @Saint-Geours2015; @Tate2015; @Rozer2019; @Hosseini-Shakib2024].

The predominant method to estimate economic flood damages in a U.S. setting is with U.S. Army Corps of Engineers (USACE) or Federal Emergency Management Agency (FEMA) depth-damage functions (DDFs) [@Merz2010; @Tate2015]. These DDFs require one hazard input - the max inundation caused by a flood relative to grade at a specific location.  In this DDF paradigm,  flood-risk estimates are sensitive to several exposure and vulnerability characteristics. In terms of exposure, risk estimates are sensitive to the spatial precision of linking a structure to a certain flood depth, the first-floor elevation of a structure, the structure's foundation type, the number of stories of the structure, the main function of the structure (i.e. residential or commercial), and the value of the structure. In terms of vulnerability, risk estimates are sensitive to the expected damage for a given depth and the shape of the depth-damage relationship. With enough effort, most structure characteristics can be represented with no uncertainty (i.e. number of stories) or negligible uncertainty due to small irreducible measurement error (i.e. first-floor elevation) [@Xia2024]. However, structure value is subject to irreducible measurement and modeling uncertainty [@Krause2020]. Similarly, DDFs are subject to irreducible measurement and modeling uncertainty [@Rozer2019; @Wing2020].

We are not aware of published free, open-source, and efficient tools for representing exposure and vulnerability under uncertainty for flood-risk estimation in the United States. The closest tool to meeting this need is the “go-consequences” tool, described as “a lightweight consequences computational engine written in Go” on its [GitHub page](https://github.com/USACE/go-consequences). Developed by the USACE, it appears that analysts can use go-consequences to produce stochastic representations of some exposure and vulnerability characteristics in the DDF paradigm. However, go-consequences does not have an official release and currently does not have documentation on example usage. “Go-consequences” was used as the basis for estimating flood risk in a 2022 Nature Climate Change paper [@Wing2022]. The [corresponding repository](https://github.com/HenryGeorgist/go-fathom) for this study states that uncertainty in first-floor elevation and vulnerability in terms of damages for a given depth were accounted for. This suggests that uncertainties in other exposure characteristics and in the shape of DDFs are not represented. In addition, statistical analyses suggest DDFs are less precise than the narrow bounds used in that study so it is possible that expected damages for a given depth could be represented with larger uncertainty bounds.

A few published free and open-source tools are available. For example, the [Hazus](https://www.fema.gov/flood-maps/products-tools/hazus) tool by FEMA is free, but is provided as a GIS-based desktop application (i.e. faces performance bottlenecks) for Windows and cannot be easily modified to accommodate uncertainty in exposure and vulnerability. The documentation states it is mostly open-source, but it is not clear if or how users can modify the program. Built on Hazus, FEMA developed the [“Flood Assessment Structure Tool”](https://github.com/nhrap-hazus/FAST?tab=readme-ov-file) to facilitate more efficient Hazus analyses in Python. This was designed for deterministic analyses. In addition, this tool now appears deprecated. The USACE maintains two published tools. Two of these tools ([HEC-FIA](https://www.hec.usace.army.mil/confluence/fiadocs/fiaum/latest) and [HEC-FDA](https://www.hec.usace.army.mil/software/hec-fda/documentation/CPD-72_V1.4.1.pdf)) appear primarily designed for internal users since the documentations state that technical support cannot be provided for non-Corps users and the software must be used as-is. Another tool worth mentioning is the advanced [Delft-FIAT (Fast Impact Assessment Tool)](https://deltares.github.io/Delft-FIAT/stable/) developed and maintained by Deltares. Like the other tools mentioned here, it currently does not accommodate flood risk estimation with uncertainty in exposure and vulnerability inputs.

The Uncertain Structure and Fragility Ensemble (UNSAFE) framework aims to fill the need for a published, free, and open-source tool for representing exposure and vulnerability under uncertainty for property-level flood-risk estimation in the U.S. 

# Overview
UNSAFE modifies a property-level risk assessment framework common in academic research and practice (e.g. Federal Emergency Management Agency (FEMA) loss avoidance studies, United States Army Corps of Engineers (USACE) feasibility studies). 


# References