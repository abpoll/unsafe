# UNSAFE: An UNcertain Structure And Fragility Ensemble framework for property-level flood risk estimation

[![Version](https://img.shields.io/badge/version-0.2.2-blue.svg)](https://github.com/abpoll/unsafe)
[![License](https://img.shields.io/badge/License-BSD--2--Clause-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintenance-Active-brightgreen.svg)](Maintenance)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.07527/status.svg)](https://doi.org/10.21105/joss.07527)


**UNSAFE** is an open-source framework for estimating property-level flood risk that explicitly accounts for uncertainties in exposure and vulnerability.

## Table of Contents
- [Overview](#overview)
- [Statement of Need](#statement-of-need)
- [Installation](#installation)
- [Examples](#examples)
- [Documentation](#documentation)
- [Contributions](#contributions)
- [License](#license)
- [Citation](#citation)
- [Acknowledgements](#acknowledgements)

## Overview
The Uncertain Structure and Fragility Ensemble (**UNSAFE**) framework enhances a property-level risk assessment framework common in academic research and practice (_e.g._, [Federal Emergency Management Agency (FEMA) loss avoidance studies](https://www.fema.gov/grants/mitigation/loss-avoidance-studies), [United States Army Corps of Engineers (USACE) feasibility studies](https://www.nad.usace.army.mil/Portals/40/docs/NACCS/10A_PhysicalDepthDmgFxSummary_26Jan2015.pdf)). At a high-level, **UNSAFE**:

1. Adds parametric uncertainty to the National Structure Inventory dataset (uncertainty in exposure)
2. Facilitates the use of multiple, potentially conflicting, expert-based Depth-Damage Functions (uncertainty in vulnerability)
3. Provides a consistent framework for estimating flood damages from any inundation model output

## Statement of Need

Flooding is a frequent, widespread, and damaging natural hazard in the United States. Research and practice increasingly estimate economic flood damage at the property level to inform management practices and policies. Economic flood damage is often estimated as a function of: 

* **Hazard**: The features of a flood over space and time 
* **Exposure**: The assets that experience inundation from a flood
* **Vulnerability**: The susceptibility of exposed assets to damage for a set of flood feature

Property-level economic flood risk assessments often overlook uncertainty in these inputs. When uncertainty is incorporated, it is more common to account for uncertainty in flood hazard than in exposure or vulnerability. Although it is a common finding that flood risk estimates are most sensitive to uncertainty in flood hazard estimates, overlooking uncertainty in exposure and vulnerability can bias risk estimates.

**UNSAFE** aims to fill the need for a published, free, and open-source tool for representing exposure and vulnerability under uncertainty for flood-risk estimation in the U.S.
We invite others to contribute to this project to help standardize best practices in the estimation of flood risk under uncertainty, improve reusability and efficiency, expand functionality for more use-cases, and maintain a state-of-the-art risk estimation codebase that is free and usable by any interested party.

## Installation

There are two ways to install **UNSAFE**.

### Option 1: For Users
If you just want to use **UNSAFE**, install with
`pip install git+https://github.com/abpoll/unsafe`.

### Option 2: For Developers
If you want to edit the source code and/or run examples:

1. Clone the repository into your project directory:
    ```bash
    git clone https://github.com/abpoll/unsafe.git
    cd unsafe
    ```
2. Create and activate the environment
    ```bash
    conda env create -f examples/env/environment.yml
    conda activate unsafe
    ```
3. Install **UNSAFE** in development mode:
    `pip install -e .`

## Examples

### Tutorials
We provide annotated, comprehensive [examples](https://github.com/abpoll/unsafe/tree/main/examples) to help get you started:

1. Partial Data Example: A tutorial with all the required data included in the repository. 
    * [Location](https://github.com/abpoll/unsafe/tree/main/examples/phil_frd_partial): `examples/philadelphia_frd/notebooks/partial_data_example.ipynb`
2. Full Data Example: A more comprehensive example that requires an external data download
    * [Location](https://github.com/abpoll/unsafe/tree/main/examples/philadelphia_frd): `examples/philadelphia_frd/notebooks/full_data_examples.ipynb`

We recommend reading the `README.md` in the root of the `examples/` directory before working through either example. 

### Published examples
For more complete examples, you can check out the following repositories for projects in different study areas and with different goals using `UNSAFE`:

* <https://github.com/abpoll/j40_gc> (Version 0.1)
* <https://github.com/abpoll/nsi_fit> (Version 0.2)

### Testing
We are working on creating automated tests, but in the meantime please run the partial data example when you start working with `UNSAFE` to verify the functionality of the package and that you have set up your machine to run it. You can verify outputs for the partial data example [here](https://htmlpreview.github.io/?https://github.com/abpoll/unsafe/blob/main/examples/phil_frd_partial/notebooks/partial_data_example.html) and the full data example [here](https://htmlpreview.github.io/?https://github.com/abpoll/unsafe/blob/main/examples/philadelphia_frd/notebooks/full_data_example.html). Note that because `UNSAFE` samples stochastically, your figures and results might look slightly different than the ones here - but they should look similar. 

## Documentation
* **Technical Documentation**: Available in the `docs/` directory, currently `v01.pdf`, which you can access [here](https://github.com/abpoll/unsafe/blob/main/docs/v01.pdf).
* **API Reference**: Coming soon! We're working on making the documentation more modern, including a comprehensive API documentation. 

## Contributions

We warmly welcome contributions from the community!
If you're interested in contributing to **UNSAFE**, we'd love to have you involved. Please check out the [guidelines for contributing](https://github.com/abpoll/unsafe/blog/main/CONTRIBUTING.md).

Feel free to engage with the development team on GitHub - we're excited to collaborate with you.

To get started, simply fork the repository and run `pip install -e .` from the project root to set up your local environment for testing and development.

We look forward to working with you to make **UNSAFE** even better!

## License
This project is licensed under the BSD-2-Clause License. Please see the [LICENSE](https://github.com/abpoll/unsafe/blob/main/LICENSE) file for details. 

## Citation
**UNSAFE** has been published at the Journal of Open Source Software (JOSS). If you use **UNSAFE** in your research, please [cite the paper](./CITATION.cff).

### Citation String
```
Pollack et al., (2025). UNSAFE: An UNcertain Structure And Fragility Ensemble framework for property-level flood risk estimation. Journal of Open Source Software, 10(115), 7527, https://doi.org/10.21105/joss.07527
```

### Bibtex
```
@article{Pollack2025,
    doi = {10.21105/joss.07527},
    url = {https://doi.org/10.21105/joss.07527},
    year = {2025},
    publisher = {The Open Journal},
    volume = {10},
    number = {115},
    pages = {7527},
    author = {Pollack, Adam and Doss-Gollin, James and Srikrishnan, Vivek and Keller, Klaus},
    title = {UNSAFE: An UNcertain Structure And Fragility Ensemble framework for property-level flood risk estimation},
    journal = {Journal of Open Source Software} 
} 
```

## Acknowledgements

Contributions to the initial v0.1 of UNSAFE
* AP: conceptualization, software development, software testing, project management, JOSS paper original draft, JOSS paper review and editing
* JDG: conceptualization, software testing, methodology, JOSS paper review and editing
* VS: conceptualization, methodology, JOSS paper review and editing
* KK: conceptualization, methodology, JOSS paper review and editing