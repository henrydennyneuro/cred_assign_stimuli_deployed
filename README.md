# Dendritic Coupling OpenScope Project Deployment Scripts

This repository contains the stimulus scripts used to generate the stimuli for the **Dendritic Coupling project**, an [Allen Institute for Brain Science](https://alleninstitute.org/what-we-do/brain-science/) [OpenScope](https://alleninstitute.org/what-we-do/brain-science/research/mindscope-program/openscope/) project. 
&nbsp;

The Dendritic Coupling experiment was conceptualized by [Joel Zylberberg](http://www.jzlab.org/) (York University), [Blake Richards](http://linclab.org/) (McGill University), and the stimuli were initially coded by [Colleen Gillon](https://sites.google.com/mila.quebec/linc-lab/team/colleen?authuser=0) and modified by [Henry Denny](https://twitter.com/hdennyneuro).

These scripts **have been updated** since [Gillon _et al._, 2021, _bioRxiv_](https://www.biorxiv.org/content/10.1101/2021.01.15.426915v2). For the exact scripts used in the experiments reported in that paper, see the [commit tagged as `production_v1`](https://github.com/colleenjg/cred_assign_stimuli_deployed/tree/production_v1). 
&nbsp;

**NOTE:** Whereas _this_ repository contains the **exact scripts** deployed for data collection in the OpenScope pipeline, the [`cred_assign_stimuli`](https://github.com/colleenjg/cred_assign_stimuli) repository contains the same base code, but modified to allow users to conveniently visualize, reproduce and save the stimuli used in [Gillon _et al._, 2021, _bioRxiv_](https://www.biorxiv.org/content/10.1101/2021.01.15.426915v2). It also contains a more detailed description of the stimulus design.  

## Stimulus design
Sparse Gabor sequences (adapted from [Homann _et al._, 2022, _PNAS_](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8812573/))
&nbsp;

## Installation
### Dependencies:
- Windows OS (see **Camstim package**)
- python 2.7
- psychopy 1.82.01
- camstim 0.2.4
&nbsp;

### Camstim 0.2.4: 
- Built and licensed by the [Allen Institute](https://alleninstitute.org/).
- Written in **Python 2** and designed for **Windows OS** (requires `pywin32`).
- Pickled stimulus presentation logs are typically saved under `user/camstim/output`.
&nbsp;

### Installation with [Anaconda](https://docs.anaconda.com/anaconda/install/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html):
1. Navigate to repository and install conda environment.  
    `conda env create -f dendri_coupl_stimuli.yml`
2. Activate the environment.  
    `conda activate cred_assign_stimuli`
3. Install the Allen Institute's `camstim` package in the environment.  
    `pip install camstim/.`
4. Download and install [`AVbin`](https://avbin.github.io/AVbin/Download.html) for your OS.  
&nbsp;

## Scripts  
### `pilot_scripts` : scripts used for deployment
- `full_pipeline_script` : Contains flexible scripts that determines the session type, and generates a suitable hapituation or ophys presentation. When running locally, parameters parameters should be recieved from `localtestregimen` using the following command:
`>python full_pipeline_script.py --json_path localtestregimen.yaml`.  
- `localtestregimen` : scripts used to set durations for each stimulus. Full length presentation totalled 70 minutes.
&nbsp;

### `production_scripts` : scripts used for the production deployment
_Not yet created._
&nbsp;

## Log files
- Pickled stimulus presentation logs are typically saved under `user/camstim/output`.
- Sweep parameters are under a few keys of `['stimuli'][n]`, where `n` is the stimulus number.
- Stimulus parameters are in dictionaries stored under: `['stimuli'][n]['stim_params']`.  
&nbsp;

## Reproduction
- There are several randomly generated components to the stimuli in each session:  
> 1) Gabor positions and sizes,  
> 2) Gabor sequence block order, 
> 3) Gabor sequence orientations,  
> 4) Unexpected event ("surprise") onsets and duration.
- The stimuli can be reproduced using the **recorded seed**, as the random state is used to generate all 4 random components.
- The same display size must be reused during reproduction.

## Code
Code and documentation (excluding `camstim`) built by Colleen Gillon (colleen _dot_ gillon _at_ mail _dot_ utoronto _dot_ ca).

