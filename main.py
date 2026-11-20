import json
import argparse
import numpy as np
from data.loader import load
from data.model import Model
from gfx.mysim import MySim
   
def load_parameters(path):
    with open(path) as file:
        return json.load(file)

# get the height data file location
parser = argparse.ArgumentParser()
parser.add_argument("data", help="path to height data")
args = parser.parse_args()

# load the height data from file
height_data = load(args.data)

### default parameters ###
parameters = load_parameters("./parameters/default.json")

# create the model from the parameters
model = Model(height_data, parameters)

# create the sim and run
screen_width = 800
screen_height = 600
screen_title = "FIRE SIMULATOR!"
mySim = MySim(screen_width, screen_height, screen_title, model)
mySim.run()




