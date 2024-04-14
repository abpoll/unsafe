# Uncertain Structure and Fragility Ensemble (UNSAFE) framework for property-level flood risk estimation
This repository hosts the latest UNSAFE version. It also includes example code that demonstrates a workflow for using UNSAFE with flood inundation model outputs to estimate property-level flood risks.

## Statement of need
Flooding is a frequent, widespread, and damaging natural hazard in the United States. Property-level economic flood risk estimates are increasingly used in research and practice to help inform management practices and policies. Economic flood risk is estimated as a function of hazard (i.e. the features of a flood over space and time), exposure (i.e. the assets that experience inundation from a flood), and vulnerability (i.e. the susceptibility of exposed assets to damage for a set of flood features).

It is common for property-level economic flood risk assessments to overlook uncertainty in these inputs. When uncertainty is incorporated, it is more common to account for uncertainty in flood hazard than in exposure or vulnerability. While it is a common finding that flood risk estimates are most sensitive to uncertainty in flood hazard estimates, overlooking uncertainty in exposure and vulnerability can bias risk estimates.

The Uncertain Structure and Fragility Ensemble (UNSAFE) framework aims to fill the need for a published, free, and open-source tool for representing exposure and vulnerability under uncertainty for flood-risk estimation in the U.S. We invite others to contribute to this project to help standardize best practices in the estimation of flood risk under uncertainty, improve reusability and efficiency, expand functionality for more use-cases, and maintain a state-of-the-art risk estimation codebase that is free and usable by any interested party.

## Overview
UNSAFE modifies a property-level risk assessment framework common in academic research and practice (e.g., [Federal Emergency Management Agency (FEMA) loss avoidance studies](https://www.fema.gov/grants/mitigation/loss-avoidance-studies), [United States Army Corps of Engineers (USACE) feasibility studies](https://www.nad.usace.army.mil/Portals/40/docs/NACCS/10A_PhysicalDepthDmgFxSummary_26Jan2015.pdf)). At a high-level, UNSAFE allows users to add parametric uncertainty to the widely used [National Structure Inventory dataset](https://www.hec.usace.army.mil/confluence/nsi/technicalreferences/2019/technical-documentation) (i.e. uncertainty in exposure), and facilitates the use of multiple, potentially conflicting, expert-based DDFs (i.e. uncertainty in vulnerability). 

We provide an extensive technical documentation in the `docs/` subdirectory. The current version is `docs/v01.pdf`

## Examples
The expected use case for UNSAFE is provided as a tutorial in the `examples/philadelphia_frd/notebooks/partial_data_example.ipynb` notebook. A more complete example is provided in  `examples/philadelphia_frd/notebooks/full_data_examples.ipynb` and illustrates how accounting for uncertainty in exposure and vulnerability can result in a substantially different representation of expected flood damages than the standard approach. This example is slightly more difficult to follow because it requires you to download data from an external source. In contrast, if you have successfuly installed unsafe into your working environment, you can immediately run the partial data example. 

## Installation
You can `pip install` the package. 

## Contributions
Contributions are very welcome! Interested parties are encouraged to engage with the development team on GitHub. 

If you would like to contribute, you can clone the package, and from the project root you can call `pip install -e .` to begin local testing and development.