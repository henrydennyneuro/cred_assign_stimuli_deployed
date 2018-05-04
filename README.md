This repo contains code to generate stimuli for our colleagues at Allen Institute Brain Science (AIBS) to use.

Specifically, the stimuli will be:
1. Sparse Gabor sequences
2. Optic flow mismatch bricks

Stimuli based on: https://www.biorxiv.org/content/biorxiv/early/2017/10/03/197608.full.pdf
http://www.jneurosci.org/content/28/30/7520

To run:
For Gabor stimuli: gabor_exp.py
For Square stimuli: square_exp.py

Additional scripts:
ourstimuli.py - Class used to build gabors and squares.
stim_params.py - Initializes stimuli and their parameters.

Dependencies:
- python 2.7
- psychopy
- camstim

Note:
- The AIBS package camstim appears to require pywin32 and the experiments are run on Windows.

