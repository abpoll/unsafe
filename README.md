# Uncertain Structure and Fragility Ensemble (UNSAFE)
This repository hosts the latest UNSAFE version. It also includes example code that demonstrates a workflow for using UNSAFE with flood inundation model outputs to estimate property-level flood risks.

<br>

## Statement of need
Flooding is a frequent, widespread, and damaging natural hazard in the United States. Economic flood risk estimates are increasingly used in research and practice to help inform management practices and policies. Economic flood risk is estimated as a function of hazard (i.e. the features of a flood over space and time), exposure (i.e. the assets that experience inundation from a flood), and vulnerability (i.e. the susceptibility of exposed assets to damage for a set of flood features). 
<br>
There is increasing demand for flood risk estimates at the scale of individual assets. This is due to the large number of decisions that can be informed by these estimates, such as insurance premium rates and risk reduction interventions to houses. In addition, flood risk estimates at coarser scales are subject to aggregation bias if the tails of the distributions of key drivers are not represented. It is easiest to capture these parts of the distributions by estimating flood risk at the property level and then aggregating. However, due to limitations in observing drivers of flood risk at this scale, and measurement and modeling error of hazard, exposure, and vulnerability when observations are available at the scale of individual assets, it is crucial that flood risk estimates account for uncertainty in key inputs. 
<br>
Flood risk estimation workflows occasionally include detailed uncertainty characterization of flood hazard inputs, but it is extremely uncommon that uncertainty in exposure or vulnerability inputs are represented. While it is commonly believed that flood risk estimates are most sensitive to uncertainty in flood hazard estimates, this does not justify the widespread lack of flood-risk estimates that account for uncertainty in exposure and vulnerability. 
<br>
We are not aware of published free, open-source, and efficient tools for representing exposure and vulnerability under uncertainty for flood-risk estimation in the United States. A few published free and open-source tools are available. For example, the [Hazus](https://www.fema.gov/flood-maps/products-tools/hazus) tool by the Federal Emergency Management Agency (FEMA) is free and mostly open-source, but is provided as a GIS-based desktop application (i.e. faces performance bottlenecks) for Windows and cannot be easily modified to accommodate uncertainty in exposure and vulnerability. FEMA developed the [“Flood Assessment Structure Tool”](https://github.com/nhrap-hazus/FAST?tab=readme-ov-file) to facilitate more efficient Hazus analyses in Python, but was designed for deterministic analyses. In addition, this tool now appears deprecated. The United States Army Corps of Engineers (USACE) maintains two tools. Two of these tools ([HEC-FIA](https://www.hec.usace.army.mil/confluence/fiadocs/fiaum/latest) and [HEC-FDA](https://www.hec.usace.army.mil/software/hec-fda/documentation/CPD-72_V1.4.1.pdf)) appear primarily designed for internal users since the documentations state that technical support cannot be provided for non-Corps users and the software must be used as-is. Another tool worth mentioning is the advanced [Delft-FIAT (Fast Impact Assessment Tool)](https://deltares.github.io/Delft-FIAT/stable/) developed and maintained by Deltares. Its main limitation is that it currently does not accommodate flood risk estimation with uncertainty in exposure and vulnerability inputs. The last tool worth mentioning is called “go-consequences,” described as “a lightweight consequences computational engine written in Go” on its [GitHub page](https://github.com/USACE/go-consequences). Developed by the USACE, it appears that analysts can use go-consequences to produce stochastic representations of exposure and vulnerability. However, go-consequences does not have an official release and currently does not have documentation on example usage. “Go-consequences” was used as the basis for estimating flood risk in a [2022 Nature Climate Change paper](https://github.com/HenryGeorgist/go-fathom) which states uncertainty in first-floor elevation and vulnerability were accounted for. 
<br>
The Uncertain Structure and Fragility Ensemble (UNSAFE) framework aims to fill the need for a published, free, open-source, and efficient tool for representing exposure and vulnerability under uncertainty for flood-risk estimation in the U.S. It is built in Python because it is a commonly used programming language and increases the odds that the functionality in UNSAFE can be easily integrated with the advanced Delft-FIAT tool. We invite others to contribute to this project to help standardize best practices in the estimation of flood risk under uncertainty, improve reusability and efficiency, expand functionality for more use-cases, and maintain a state-of-the-art risk estimation codebase that is free and usable by any interested party. 
<br>

## Overview
The guiding principle of UNSAFE is transparency. [Transparency on the basis of uncertainty characterization, how distributions are specified, etc.]
Structure

## Recommended Use

## Installation

## Examples

## Contributions

### Initial contributions to v0.1
