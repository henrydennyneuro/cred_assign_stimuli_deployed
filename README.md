# Original Credit Assignment OpenScope Project Stimulus Generation Scripts

This repository contains the original code used to generate the stimuli for the **Credit Assignment project**, an [Allen Institute for Brain Science](https://alleninstitute.org/what-we-do/brain-science/) [OpenScope](https://alleninstitute.org/what-we-do/brain-science/news-press/press-releases/openscope-first-shared-observatory-neuroscience) project. 
&nbsp;

The Credit Assignment experiment was conceptualized by [Joel Zylberberg](http://www.jzlab.org/) (York University), [Blake Richards](http://linclab.org/) (McGill University), [Timothy Lillicrap](http://contrastiveconvergence.net/~timothylillicrap/index.php) (DeepMind) and [Yoshua Bengio](https://yoshuabengio.org/) (Mila), and the stimuli were coded by [Colleen Gillon](https://sites.google.com/mila.quebec/linc-lab/team/colleen?authuser=0).

The experiment details, analyses and results are published in [Gillon _et al._, 2021, _bioRxiv_](https://www.biorxiv.org/content/10.1101/2021.01.15.426915v2). 
&nbsp;

## Stimulus design
1. Sparse Gabor sequences (adapted from [Homann _et al._, 2017, _bioRxiv_](https://www.biorxiv.org/content/biorxiv/early/2017/10/03/197608.full.pdf))
2. Visual flow mismatch ("bricks") (pilot and production v1 only)
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
    `conda env create -f cred_assign_stimuli.yml`
2. Activate the environment.  
    `conda activate cred_assign_stimuli`
3. Install the AIBS `camstim` package in the environment.  
    `pip install camstim/.`
4. Download and install [`AVbin`](https://avbin.github.io/AVbin/Download.html) for your OS.  
&nbsp;

## Scripts  
### `pilot_scripts` : scripts used for the pilot deployment
- `habituation_rig` : scripts used on the habituation rig. For each habituation day, a different script is used, shared across all subjects,  
e.g., run `python pilot_scripts/habituation_rig/day7.py`.  
- `ophys_rig` : scripts used on the optical physiology rig. For each subject, a different script is used,   
e.g., run `python pilot_scripts/ophys_rig/stim_Mouse3_2p.py`.  
&nbsp;

### `production_scripts` : scripts used for the production deployment
- `habituation_rig` : scripts used on the habituation rig. For each habituation day, a different script is used, shared across all subjects,  
e.g., run `python production_scripts/habituation_rig/day7.py`.  
- `ophys_rig` : scripts used on the optical physiology rig. For each experiment day, a different script is used, shared across all subjects,  
e.g., run `python production_scripts/ophys_rig/ophys_record.py`.  
&nbsp;

## Log files
- Pickled stimulus presentation logs are typically saved under `user/camstim/output`.
- Sweep parameters are under a few keys of `['stimuli'][n]`, where `n` is the stimulus number.
- Stimulus parameters are in the following dictionary: `['stimuli'][0]['stimParams']` or `['stimuli'][0]['stim_params']`.  
&nbsp;

## Reproduction
- There are several randomly generated components to the stimuli in each session:  
> 1) Gabor positions and sizes,  
> 2) Stimulus order, 
> 3) Gabor sequence orientations,  
> 4) Visual flow square ("brick") positions (pilot and production v1 only),  
> 5) Unexpected event ("surprise") onsets and duration.
- **Production stimuli (v2)** can be reproduced using **recorded seed** as the random state is used to generate all 5 random components.
- **Pilot stimuli** cannot be so easily reproduced as the **recorded seed** (100 or 103, depending on the subject) **only controls the first random component (1)**. All other random components are initialized using unseeded random states.
- The same display size must be reused during reproduction.

