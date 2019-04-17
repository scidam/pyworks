from tqdm import tqdm
import requests
import itertools
import os
import time

CHUNK_SIZE = 10 ** 6 # Chunk size in bytes
TIMEOUT = 0.1 # The bigger this value, the lesser average speed of data loading

BASE_URL = "http://biogeo.ucdavis.edu/data/climate/"

OUTPUT_DIR =  "data" # A path where the data being loading



# ------------------- Components of data file path ------------------

# current climate
current_cmps = [
    ['worldclim/1_4/grid/cur'], 
    ['30s'],
    ['bil'],
    ['tmin', 'tmax', 'prec', 'tmean', 'bio1-9', 'bio10-19'],
    ['.zip']
]


# past climate
past_cmps = [
            ['cmip5/'], 
            ['mid', 'lgm'], #epoch
            ['30s', '2-5m'],
            ['cc', 'mr'], #model name
            #['bc', 'cc', 'cn', 'hg', 'he', 'ip', 'mr', 'me', 'mg'], #model name
            ['bi', 'pr', 'tn', 'tx'],
            ['.zip']
            ]

# future climate
future_cmps = [
['cmip5/'], 
['50', '70'], #epoch
['30s'],
['cc', 'mr'], #model name: we need cc model only!
#['ac', 'bc', 'cc', 'ce', 'cn', 'gf', 'gd','gs', 'hd', 'hg', 'he', 'in', 'ip', 'mi', 'mc', 'mp', 'mr', 'mg', 'no'], #model name
['26', '45', '60', '85'], # CO2
['bi', 'pr', 'tn', 'tx'],
['.zip']
]


def try_or_load(cmps, name='current'):
    """Load data if they exist
    
    Parameters
    ==========
        cmps  -- a tuple, data components

    """
    url_cmp = cmps[0]

    if name == 'current':
        resolution = cmps[1]
        gis_ext = cmps[2]
        variable_name = cmps[3]
        ext = cmps[4]
        url = BASE_URL + url_cmp + "/{}_{}_{}{}".format(variable_name, resolution, gis_ext, ext)
        dirpath = os.path.join(OUTPUT_DIR, "current", variable_name)
    elif name == 'past':
        url_cmp = cmps[0]
        epoch = cmps[1]
        resolution = cmps[2]
        model_name = cmps[3]
        variable_name = cmps[4]
        ext = cmps[5]
        url = BASE_URL + url_cmp + '{}/{}{}{}_{}{}'.format(epoch, model_name, epoch, variable_name, resolution, ext)
        dirpath = os.path.join(OUTPUT_DIR, "past", model_name, epoch, variable_name)
    elif name == 'future':
        url_cmp = cmps[0]
        epoch = cmps[1]
        resolution = cmps[2]
        model_name = cmps[3]
        co2 = cmps[4]
        variable_name = cmps[5]
        ext = cmps[6]
        url = BASE_URL + url_cmp + '{}/{}{}{}{}{}'.format(resolution, model_name, co2, variable_name, epoch, ext)
        dirpath = os.path.join(OUTPUT_DIR, "future", model_name, epoch, co2, variable_name)
    else:
        print("Nothing to load. Exiting...")

    with requests.get(url, stream=True) as response:
        if response.status_code == 200:
            print("Processing url: {}".format(url))
            filename = os.path.basename(url)
            os.makedirs(os.path.dirname(os.path.join(dirpath, filename)), exist_ok=True)
            if not os.path.exists(os.path.join(dirpath, filename)):
                with open(os.path.join(dirpath, filename), "wb") as writer:
                    for data in tqdm(response.iter_content(chunk_size=CHUNK_SIZE), unit_scale=CHUNK_SIZE/10**6, unit='MB'):
                        writer.write(data)
                        time.sleep(TIMEOUT)
        else:
            print("Url: {} doesn't exist".format(url))


# ------------ Load current data -----------

# load future climatic data
for cmps in itertools.product(*future_cmps):
    try_or_load(cmps, name='future')

# load current climatic data 
for cmps in itertools.product(*current_cmps):
    try_or_load(cmps, name='current')

# load past climatic data
for cmps in itertools.product(*past_cmps):
    try_or_load(cmps, name='past')    
