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
Unfortunately, $\tilde{z}_{a(i)}^s$, $v_i$, and $D$ are imperfectly observed and/or modeled. The NSI does not clarify which records in the structure inventories are of high or low quality. In addition, there is a limited understanding of how well expert-based DDFs produced by FEMA or the USACE accurately or consistently reproduce real-world depth-damage relationships. 

