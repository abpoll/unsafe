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

## Standard theoretical framework for property-level flood-loss estimation
Flooding reduces the value of affected structures by a damage amount, $L_i$. $L_i$ is the product of the value of a structure, $v_i$, and a damage relationship, $D$. This relationship, often specified as a depth-damage function (DDF), translates the inundation depth, $x_i$, faced by an affected structure based on characteristics of the affected structure (given by the vector $z_i^s$) into the fraction of value lost. U.S. agencies such as FEMA and the USACE develop DDFs using engineering expert judgement to derive depth-damage relationships for so-called archetypes, $a(i)$, that map broad groups of observed house characteristics, $\tilde{z}_{a(i)}^s$, into categories of point-estimate based depth-damage relationships. These DDFs are defined such that depth is related to loss in an increasing, monotonic shape meaning that each additional unit of inundation results in more damage to a structure. Archetypes consist of the foundation typ, $fnd\_type_i$, number of stories, $num\_story_i$, and $occ\_type_i$ (i.e. residential or commercial occupancy) of a structure. The vector $z_i^s$ also consists of the structure's first-floor elevation. The difference of this vector, $ffe_i$, from $x_i$ yields the inundation that is the input to a DDF. The standard loss estimation model can thus be represented as: 

$$ L_i = D[x_i, \tilde{z}_{a(i)}^s]*v_i$$

## Standard way to operationalize this approach
The most common way analysts operationalize the standard theoretical framework is through point-based representations of vulnerability and exposure through expert-based DDFs, and the USACE National Structure Inventory, respectively. According to its [technical documentation](https://www.hec.usace.army.mil/confluence/nsi/technicalreferences/latest/technical-documentation), the NSI [**emphasis ours**] "is a system of databases containing structure inventories of varying quality and spatial coverage. The purpose of the NSI databases is to facilitate storage and sharing of **point based** structure inventories used in the assessment and analysis of natural hazards."

The NSI represents each structure's:
* (x,y) coordinates in Geographic Coordinate System (GCS) WGS84 which are needed to link structures to flood hazard, and
* characteristics needed for flood-loss estimation ($occ\_type_i$, $fnd\_type_i$, $ffe_i$, $num\_story_i$, $v_i$)

The NSI records are used as-is to prepare inputs to DDFs for a single estimate of flood damage for each structure.

## Incorporating uncertainty into the standard approach
This standard approach neglects observation and/or model unceratinty in $\tilde{z}_{a(i)}^s$, $v_i$, and $D$. The NSI does not clarify which records in the structure inventories are of high or low quality. In addition, there is a limited understanding of how well expert-based DDFs produced by FEMA or the USACE accurately or consistently reproduce real-world depth-damage relationships. 

In the current implementation, UNSAFE adds uncertainty to the standard exposure (i.e NSI) and vulnerability (i.e. expert DDFs) inputs for property-level flood risk assessments in the U.S. In the future, we plan for UNSAFE to treat the current implementation as a benchmark approach, and allow for arbitrary data input to represent any component of the loss-estimation framework. 

### Uncertainty in exposure
UNSAFE calls the NSI API, downloads the structure inventory, and treats the spatial coordinates and $occ\_type_i$ of each record as-is. Currently, UNSAFE is designed to work for single-family houses ($occ\_type_i = $ 'RES1'). From this base inventory, UNSAFE generates a $J$ member ensemble of plausible realizations of key variables for each structure. We define the distributions that ensemble members are drawn from based on guidance in the NSI and peer-reviewed academic literature.

#### Structure value
$$
    {v}_{i}\sim 
\begin{dcases}
    N(NSI\_val_i, .2*NSI\_val_i) & \text{if $v_{i,j} \geq 1 $} \\
    1                            & otherwise
\end{dcases}
$$
where $NSI\_val_i$ is the structure value provided in the NSI record as-is. 

The NSI represents structure value as depreciated replacement values. These are estimated based on an assumed replacement category and a dollar per square footage estimate for that category. According to the NSI documentation, these are informed by an "analysis of survey data, parcel use types, and other source inputs." There is no documentationon what the replacement categories are, or what the dollar per square footage estimates for these categories are. Values are in 2021 price levels. Dollars per square foot are multiplied by square footage estimates from building footprint data to obtain a structure value estimate. Replacement values are depreciated according to a 1\% per year schedule for the 1st 20 years and it is assumed there is no further depreciation. 

Due to the lack of transparency in the NSI documentation, it is unclear what the underlying distribution for structure values are. We assume a distributional form that produces normally distributed noise around the NSI records. We make the generous assumption that the NSI structure value records are mean unbiased and are as precise as state-of-the-art automated valuation models for property market transactions (See `joss_submission/paper.md` for more information). We use a piecewise distribution to left-censor draws from the normal distribution at $1 because it is illogical to have structure values below $1. In the case study provided in `examples/` the lowest structure value is $92,695 and it is extremely unlikely that values below $1 are drawn (i.e. the probability of drawing a value less than $25,000 is 0.0001).     

#### Number of stories

$$
num\_story_{i} \sim binomial (J, p^{tract}) 
$$

where $p^{tract}$ is the proportion of residential structures with 1 story in the census tract that structure $i$ is located in. In the current implementation of UNSAFE, DDFs for residential houses are for 1 and 2 story structures, so we can use the binomial distribution. 

According to the NSI technical documentation, number of stories records are drawn from parcel data where possible. When missing, square footage for single family homes (RES1 category) is estimated by taking 86\% of a structure's footprint. This percentage was estimated at a nationwide level using available parcel, survey, and footprint datasets. If no footprint is available, sq. ft. is randomly assigned "from a distribution that varies by the structure's year built and census region." If \# stories is not available for RES1, it is estimated by dividing the estimated sq. ft. by the structure's footprint, where any decimal greater than .25 after a digit leads to rounding up the \# of story estimate (i.e. 1.25 means 2 story home). If no footprint is available, \# stories is randomly assigned from a distribution that varies by year built and census region. By specifying the UNSAFE distribution at the census tract level, we capture the site-specific assignments that the underlying parcel data provides in addition to the heuristic assignments. 

#### Foundation type

$$
fnd_{i} \sim multinomial(J, p_{slab}^{tract}, p_{crawl}^{tract}, p_{basement}^{tract})
$$

where $p_{fnd\_type}^{tract}$ corresponds to the proportion of structures in the census tract that structure $i$ is located in with a given $fnd\_type$. It is uncommon, but single family residences can have other foundation types than those shown above. UNSAFE currently is designed to work in case study environments where only these foundation types are present.  

The NSI technical documentation states that foundation type is mapped from parcel data when available. When this data is not available, the foundation types are randomly assigned using the HAZUS structure inventory. The Hazus 6.0 Inventory Technical Documentation states that foundation types are based on General Building Stock distribution tables that contain the proportions of foundation type for different Census Divisions (i.e. New England or South Atlantic) based on surveys conducted in 1993, 1997, or 2000 (depending on riverine or coastal flood hazard zone). The multinomial distribution we define attempts to capture the underlying distribution that the NSI draws these values from, adjusted for records provided by parcel datasets. By specifying the UNSAFE distribution at the census tract level, we capture the site-specific assignments that the underlying parcel data provides in addition to the random assignments from the HAZUS structure inventory. We specify this distribution at the census tract level, instead of block group or block level, so that $J_{tract}$ has a sufficient sample size for specifying We note that foundation type data is relatively uncommon in parcel data sources (see `joss_submission/` for more info).

#### First-floor elevation

$$
    {ffe}_{i}= 
\begin{dcases}
    triangular(0, .5, 1.5),& \text{if $fnd_{i, j}$ = Slab}\\
    triangular(0, .5, 1.5),& \text{if $fnd_{i, j}$ = Crawl Space}\\
    triangular(0, 1.5, 4), & \text{if $fnd_{i, j}$ = Basement}
\end{dcases}
$$

According to the NSI technical documentation, foundation heights are mapped to each foundation type based on survey estimates from 2021 with each assumed height "closely matching the median value from the survey." Although the distributions that these are drawn from are not shared in the technical documentation, there is some guidance on the distributions from [this repository](https://github.com/HenryGeorgist/go-fathom/blob/master/compute/foundationheights.go), which is the basis for a [Nature Climate Change study from 2022](https://www.nature.com/articles/s41558-021-01265-6) with a co-author from the USACE. 

#### A note on NSI records informed by parcel datasets
According to the NSI documentation, foundation type and number of stories records are occasionally based on parcel datasets. Parcel datasets are likely more accurate (they may contain errors) than the random assignment from the NSI procedure. This suggests that UNSAFE may add unneeded noise to some records, and subsequently flood-loss estimates. Our view is that until the NSI technical documentation provides guidance about which records are of high quality, such as by indicating which records come from parcel data or what distributions certain records are drawn from, all records should be treated as uncertain. We acknowledge that this may lead to noisier flood-loss estimates at the structure level when records are informed by parcel datasets. However, we expect that expected property-level losses, across the ensemble generated by UNSAFE, aggregated to census tract or broader spatial scales will be less biased than if all structure records were taken as-is. 

In future versions of UNSAFE, we plan to allow users to specify base structure inventories other than the NSI. In such cases, users can indicate when records should be taken as-is, and when there is uncertainty around records due to measurement and/or model error. For example, appraiser databases may include detailed documentation on the staitical fit of automated value model used to determine depreciated replacement costs.  

### Uncertainty in vulnerability

# References