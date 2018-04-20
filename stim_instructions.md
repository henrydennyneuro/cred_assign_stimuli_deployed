It appears that camstim requires a python 2.7 environment. The production systems are running on Windows, so that is where I have done my initial testing and what the instructions are for.

I found that you may need to download and install the appropriate [avbin libraries](https://avbin.github.io/AVbin/Download.html). Unzip the zip file.

    cd <directory you unzipped to>
    pip install .

Then from wherever you have the example_stimulus.py:

    python example_stimulus.py

The example stimulus shows drifting gratings as well as loading a movie from a .npy file and using it with spherical warping applied based on the settings that will be used in the production environment.
