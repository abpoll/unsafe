# Uncertain Structure and Fragility Ensemble (UNSAFE) framework for property-level flood risk estimation
This repository hosts the latest UNSAFE version. It also includes example code that demonstrates a workflow for using UNSAFE with flood inundation model outputs to estimate property-level flood risks.

## Statement of need
Flooding is a frequent, widespread, and damaging natural hazard in the United States. Economic flood risk estimates are increasingly used in research and practice to help inform management practices and policies. Economic flood risk is estimated as a function of hazard (i.e. the features of a flood over space and time), exposure (i.e. the assets that experience inundation from a flood), and vulnerability (i.e. the susceptibility of exposed assets to damage for a set of flood features).

It is common for property-level economic flood risk assessments to overlook uncertainty in these inputs. When uncertainty is incorporated, it is more common to account for uncertainty in flood hazard than in exposure or vulnerability. While it is a common finding that flood risk estimates are most sensitive to uncertainty in flood hazard estimates, overlooking uncertainty in exposure and vulnerability can bias risk estimates.

The Uncertain Structure and Fragility Ensemble (UNSAFE) framework aims to fill the need for a published, free, and open-source tool for representing exposure and vulnerability under uncertainty for flood-risk estimation in the U.S. We invite others to contribute to this project to help standardize best practices in the estimation of flood risk under uncertainty, improve reusability and efficiency, expand functionality for more use-cases, and maintain a state-of-the-art risk estimation codebase that is free and usable by any interested party.

## Overview
UNSAFE modifies a property-level risk assessment framework common in academic research and practice (e.g. Federal Emergency Management Agency (FEMA) loss avoidance studies, United States Army Corps of Engineers (USACE) feasibility studies). 

### Standard theoretical framework for property-level flood-loss estimation
Flooding reduces the value of affected structures by a damage amount, $L_i$. $L_i$ is the product of the value of a structure, $v_i$, and a damage relationship, $D$. This relationship, often specified as a depth-damage function (DDF), translates the inundation depth, $x_i$, faced by an affected structure based on characteristics of the affected structure (given by the vector $z_i^s$) into the fraction of value lost. U.S. agencies such as FEMA and the USACE develop DDFs using engineering expert judgement to derive depth-damage relationships for so-called archetypes, $a(i)$, that map broad groups of observed house characteristics, $\tilde{z}_{a(i)}^s$, into categories of point-estimate based depth-damage relationships. These DDFs are defined such that depth is related to loss in an increasing, monotonic shape meaning that each additional unit of inundation results in more damage to a structure. Archetypes consist of the foundation typ, $fnd\_type_i$, number of stories, $num\_story_i$, and $occ\_type_i$ (i.e. residential or commercial occupancy) of a structure. The vector $z_i^s$ also consists of the structure's first-floor elevation. The difference of this vector, $ffe_i$, from $x_i$ yields the inundation that is the input to a DDF. The standard loss estimation model can thus be represented as: 

$$ L_i = D[x_i, \tilde{z}_{a(i)}^s]*v_i$$

### Standard way to operationalize this approach
The most common way analysts operationalize the standard theoretical framework is through point-based representations of vulnerability and exposure through expert-based DDFs, and the USACE National Structure Inventory, respectively. According to its [technical documentation](https://www.hec.usace.army.mil/confluence/nsi/technicalreferences/latest/technical-documentation), the NSI [**emphasis ours**] "is a system of databases containing structure inventories of varying quality and spatial coverage. The purpose of the NSI databases is to facilitate storage and sharing of **point based** structure inventories used in the assessment and analysis of natural hazards."

The NSI represents each structure's:
* (x,y) coordinates in Geographic Coordinate System (GCS) WGS84 which are needed to link structures to flood hazard, and
* characteristics needed for flood-loss estimation ($occ\_type_i$, $fnd\_type_i$, $ffe_i$, $num\_story_i$, $v_i$)

The NSI records are used as-is to prepare inputs to DDFs for a single estimate of flood damage for each structure.

 ### Incorporating uncertainty into the standard approach
This standard approach neglects observation and/or model unceratinty in $\tilde{z}_{a(i)}^s$, $v_i$, and $D$. The NSI does not clarify which records in the structure inventories are of high or low quality. In addition, there is a limited understanding of how well expert-based DDFs produced by FEMA or the USACE accurately or consistently reproduce real-world depth-damage relationships. 

In the current implementation, UNSAFE adds uncertainty to the standard exposure (i.e NSI) and vulnerability (i.e. expert DDFs) inputs for property-level flood risk assessments in the U.S. In the future, we plan for UNSAFE to treat the current implementation as a benchmark approach, and allow for arbitrary data input to represent any component of the loss-estimation framework. 

#### Uncertainty in exposure
UNSAFE calls the NSI API, downloads the structure inventory, and treats the spatial coordinates and $occ\_type_i$ of each record as-is. Currently, UNSAFE is designed to work for single-family houses ($occ\_type_i = $ 'RES1'). From this base inventory, UNSAFE generates a $J$ member ensemble of plausible realizations of key variables for each structure. We define the distributions that ensemble members are drawn from based on guidance in the NSI and peer-reviewed academic literature.

##### Structure value
$$
    {v}_{i}\sim 
\begin{dcases}
    N(NSI\_val_i, .2*NSI\_val_i) & \text{if $v_{i,j} \geq 1 $} \\
    1                            & otherwise
\end{dcases}
$$
where $NSI\_val_i$ is the structure value provided in the NSI record asi-s. 

The NSI represents structure value as depreciated replacement values. These are estimated based on an assumed replacement category and a dollar per square footage estimate for that category. According to the NSI documentation, these are informed by an "analysis of survey data, parcel use types, and other source inputs." There is no documentationon what the replacement categories are, or what the dollar per square footage estimates for these categories are. Values are in 2021 price levels. Dollars per square foot are multiplied by square footage estimates from building footprint data to obtain a structure value estimate. Replacement values are depreciated according to a 1\% per year schedule for the 1st 20 years and it is assumed there is no further depreciation. 

Due to the lack of transparency in the NSI documentation, it is unclear what the underlying distribution for structure values are. We assume a distributional form that produces normally distributed noise around the NSI records. We make the generous assumption that the NSI structure value records are mean unbiased and are as precise as state-of-the-art automated valuation models for property market transactions (See `joss_submission/paper.md` for more information). We use a piecewise distribution to left-censor draws from the normal distribution at $1 because it is illogical to have structure values below $1. In the case study provided in `examples/` the lowest structure value is $92,695 and it is extremely unlikely that values below $1 are drawn (i.e. the probability of drawing a value less than $25,000 is 0.0001).     

##### Number of stories

$$
num\_story_{i} \sim binomial (J, p^{tract}) 
$$

where $p^{tract}$ is the proportion of residential structures with 1 story in the census tract that structure $i$ is located in. In the current implementation of UNSAFE, DDFs for residential houses are for 1 and 2 story structures, so we can use the binomial distribution. 

According to the NSI technical documentation, number of stories records are drawn from parcel data where possible. When missing, square footage for single family homes (RES1 category) is estimated by taking 86\% of a structure's footprint. This percentage was estimated at a nationwide level using available parcel, survey, and footprint datasets. If no footprint is available, sq. ft. is randomly assigned "from a distribution that varies by the structure's year built and census region." If \# stories is not available for RES1, it is estimated by dividing the estimated sq. ft. by the structure's footprint, where any decimal greater than .25 after a digit leads to rounding up the \# of story estimate (i.e. 1.25 means 2 story home). If no footprint is available, \# stories is randomly assigned from a distribution that varies by year built and census region. By specifying the UNSAFE distribution at the census tract level, we capture the site-specific assignments that the underlying parcel data provides in addition to the heuristic assignments. 

##### Foundation type

$$
fnd_{i} \sim multinomial(J, p_{slab}^{tract}, p_{crawl}^{tract}, p_{basement}^{tract})
$$

where $p_{fnd\_type}^{tract}$ corresponds to the proportion of structures in the census tract that structure $i$ is located in with a given $fnd\_type$. It is uncommon, but single family residences can have other foundation types than those shown above. UNSAFE currently is designed to work in case study environments where only these foundation types are present.  

The NSI technical documentation states that foundation type is mapped from parcel data when available. When this data is not available, the foundation types are randomly assigned using the HAZUS structure inventory. The Hazus 6.0 Inventory Technical Documentation states that foundation types are based on General Building Stock distribution tables that contain the proportions of foundation type for different Census Divisions (i.e. New England or South Atlantic) based on surveys conducted in 1993, 1997, or 2000 (depending on riverine or coastal flood hazard zone). The multinomial distribution we define attempts to capture the underlying distribution that the NSI draws these values from, adjusted for records provided by parcel datasets. By specifying the UNSAFE distribution at the census tract level, we capture the site-specific assignments that the underlying parcel data provides in addition to the random assignments from the HAZUS structure inventory. We specify this distribution at the census tract level, instead of block group or block level, so that $J_{tract}$ has a sufficient sample size for specifying We note that foundation type data is relatively uncommon in parcel data sources (see `joss_submission/` for more info).

##### First-floor elevation

$$
    {ffe}_{i}= 
\begin{dcases}
    triangular(0, .5, 1.5),& \text{if $fnd_{i, j}$ = Slab}\\
    triangular(0, .5, 1.5),& \text{if $fnd_{i, j}$ = Crawl Space}\\
    triangular(0, 1.5, 4), & \text{if $fnd_{i, j}$ = Basement}
\end{dcases}
$$

According to the NSI technical documentation, foundation heights are mapped to each foundation type based on survey estimates from 2021 with each assumed height "closely matching the median value from the survey." Although the distributions that these are drawn from are not shared in the technical documentation, there is some guidance on the distributions from [this repository](https://github.com/HenryGeorgist/go-fathom/blob/master/compute/foundationheights.go), which is the basis for a [Nature Climate Change study from 2022](https://www.nature.com/articles/s41558-021-01265-6) with a co-author from the USACE. 

##### A note on NSI records informed by parcel datasets
According to the NSI documentation, foundation type and number of stories records are occasionally based on parcel datasets. Parcel datasets are likely more accurate (they may contain errors) than the random assignment from the NSI procedure. This suggests that UNSAFE may add unneeded noise to some records, and subsequently flood-loss estimates. Our view is that until the NSI technical documentation provides guidance about which records are of high quality, such as by indicating which records come from parcel data or what distributions certain records are drawn from, all records should be treated as uncertain. We acknowledge that this may lead to noisier flood-loss estimates at the structure level when records are informed by parcel datasets. However, we expect that expected property-level losses, across the ensemble generated by UNSAFE, aggregated to census tract or broader spatial scales will be less biased than if all structure records were taken as-is. 

In future versions of UNSAFE, we plan to allow users to specify base structure inventories other than the NSI. In such cases, users can indicate when records should be taken as-is, and when there is uncertainty around records due to measurement and/or model error. For example, appraiser databases may include detailed documentation on the staitical fit of automated value model used to determine depreciated replacement costs.  

#### Uncertainty in vulnerability