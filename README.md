# Uncertain Structure and Fragility Ensemble (**UNSAFE**) framework for property-level flood risk estimation

This repository hosts the latest **UNSAFE** version.
It also includes example code that demonstrates a workflow for using **UNSAFE** with flood inundation model outputs to estimate property-level flood risks.

## Statement of need

Flooding is a frequent, widespread, and damaging natural hazard in the United States.
Property-level economic flood risk estimates are increasingly used in research and practice to help inform management practices and policies.
Economic flood risk is estimated as a function of hazard (_i.e._, the features of a flood over space and time), exposure (_i.e._, the assets that experience inundation from a flood), and vulnerability (_i.e._, the susceptibility of exposed assets to damage for a set of flood features).

It is common for property-level economic flood risk assessments to overlook uncertainty in these inputs.
When uncertainty is incorporated, it is more common to account for uncertainty in flood hazard than in exposure or vulnerability.
While it is a common finding that flood risk estimates are most sensitive to uncertainty in flood hazard estimates, overlooking uncertainty in exposure and vulnerability can bias risk estimates.

The Uncertain Structure and Fragility Ensemble (**UNSAFE**) framework aims to fill the need for a published, free, and open-source tool for representing exposure and vulnerability under uncertainty for flood-risk estimation in the U.S.
We invite others to contribute to this project to help standardize best practices in the estimation of flood risk under uncertainty, improve reusability and efficiency, expand functionality for more use-cases, and maintain a state-of-the-art risk estimation codebase that is free and usable by any interested party.

## Overview

**UNSAFE** modifies a property-level risk assessment framework common in academic research and practice (_e.g._, [Federal Emergency Management Agency (FEMA) loss avoidance studies](https://www.fema.gov/grants/mitigation/loss-avoidance-studies), [United States Army Corps of Engineers (USACE) feasibility studies](https://www.nad.usace.army.mil/Portals/40/docs/NACCS/10A_PhysicalDepthDmgFxSummary_26Jan2015.pdf)).
At a high-level, **UNSAFE** allows users to add parametric uncertainty to the widely used [National Structure Inventory dataset](https://www.hec.usace.army.mil/confluence/nsi/technicalreferences/2019/technical-documentation) (_i.e._, uncertainty in exposure), and facilitates the use of multiple, potentially conflicting, expert-based DDFs (_i.e._, uncertainty in vulnerability).

We provide an extensive technical documentation in the `docs/` subdirectory.
The current version is `docs/v01.pdf`.

Head over to the examples in the `examples/` directory to see how **UNSAFE** is used in practice, and get hands-on experience with setting up a script or notebook for getting risk estimates.

## Examples

The expected use case for **UNSAFE** is provided as a tutorial in the `examples/philadelphia_frd/notebooks/partial_data_example.ipynb` notebook.
This notebook also includes detailed markdown documentation to describe the workflow.
All of the data (it's a small example) needed to run this example is included when you install **UNSAFE**.
Another example is provided in `examples/philadelphia_frd/notebooks/full_data_examples.ipynb`.
This example can be reproduced if you download data from an external source.
We include it to illustrate how accounting for uncertainty in exposure and vulnerability can result in a substantially different representation of expected flood damages than the standard approach.

## Installation

There are two ways to install **UNSAFE**.

1. If you want to edit the source code and/or run examples:

    1. `git clone` this repository to your local machine.
    1. `cd` into the repository.
    1. Using conda, install the packages required for the examples with `conda env create -f examples/env/environment.yml`.
    1. Activate the environment with `conda activate unsafe`.
    1. Run `pip install -e .` to install **UNSAFE** in editable mode.

1. If you just want to use **UNSAFE**:

    1. Install **UNSAFE** with `pip install git+https://github.com/abpoll/unsafe`.

## Contributions

We warmly welcome contributions from the community!
If you're interested in contributing to **UNSAFE**, we'd love to have you involved.
Feel free to engage with the development team on GitHub - we're excited to collaborate with you.

To get started, simply clone the package and run `pip install -e .` from the project root to set up your local environment for testing and development.
We look forward to working with you to make **UNSAFE** even better!
