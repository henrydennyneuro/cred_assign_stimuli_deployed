import os
import numpy as np
from glob import glob

def generatemovies(rawmovie):
    
    # Creates the 4 varients of each movie we require

    movie_short = rawmovie[0:270]

    #Create the movie in reverse. We can do this by slicing the first 9 seconds of the loaded movie,
    #then use the flipud function to fill a new array back-to-front from the slice we selected. 

    movie_reversed = np.flipud(movie_short)

    #Now we will create two movies that switch direction at the 3 second mark. 

    #Forward movie with reverse scrub
    fw_movie_scrubSeg1 = movie_short[0:90]
    fw_movie_scrubSeg3 = movie_short[0:90]
    fw_movie_scrubSeg2 = movie_reversed[180:270]
    fw_movie_scrub = np.concatenate((fw_movie_scrubSeg1, fw_movie_scrubSeg2, fw_movie_scrubSeg3))

    #Reverse movie with forward scrub
    bw_movie_scrubSeg1 = movie_reversed[0:90]
    bw_movie_scrubSeg3 = movie_reversed[0:90]
    bw_movie_scrubSeg2 = movie_short[180:270]
    bw_movie_scrub = np.concatenate((bw_movie_scrubSeg1, bw_movie_scrubSeg2, bw_movie_scrubSeg3))

    npymovies = {
        '0' : movie_short,
        '1' : movie_reversed,
        '2' : fw_movie_scrub,
        '3' : bw_movie_scrub 
    }

    return npymovies

loadpath = ".\\natural_movies\\"
savepath = ".\\natural_movies\\stims\\"

os.mkdir(loadpath+'stims\\')

stimulus_path_pattern = os.path.join(loadpath, '*.npy')
stimulus_paths = sorted(
    map(os.path.abspath, glob(stimulus_path_pattern))
)

nameindex = -1

for j, stimulus_path in enumerate(stimulus_paths):
    nameindex = nameindex + 1
    moviename = 'Movie'+str(nameindex)
    rawmovie = np.load(stimulus_path)
    npymovies = generatemovies(rawmovie)
    os.mkdir(savepath+str(j)+"\\")

    for key in npymovies:
        np.save(savepath+str(j)+"\\"+'Movie'+str(j)+key+'.npy', npymovies[key])

# If you try to do this for more than 9 movies or with more than 9 variations,
# this method will probably break.


