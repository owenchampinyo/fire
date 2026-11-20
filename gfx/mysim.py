from gfx.engine import GfxEngine
from random import random
import math as m
import util.math as u
import numpy as np

### PUT YOUR CUSTOM FUNCTIONS HERE ###

# simulation parameters
model_parameters = {
    "seed": 12345,                  # seed value for random generator       
    "scale": 30,                    # baseline satellite data scale
    "veg_probability": 0.9,         # baseline probability of vegitation (plants, trees etc.)
    "veg_density_decay": 1.0,         # rate of vegitation density decay with altitude, exp(-height * decay)
    "veg_humidity_decay": 2.0,        # rate of vegitation humidity decay with altitude exp(-height * decay)
    "max_ignition_time": 500,       # max time ignition can smoulder (ms)
    "max_fire_time": 2000,          # max time fire can burn (ms)
    "wind_direction": 0,            # wind direction in degrees from north (up)
    "sun_angle": 45,                # sun angle in degrees from horizon
}

### USEFUL FUNCTIONS HERE ###

clamper = u.clamp(0.05, 2)

def fire_slope(dH, scale):
    H = m.sqrt(dH * dH + scale * scale)
    return clamper(1 + 30*m.sin(dH / H))

def fire_wind(fire_wind):
    fire_direction = (other_row, other_col)- (row, col)
    module1 = m.sqrt(fire_direction[0] + fire_direction[1])
    vec.wind_direction = (m.cos(wind_direction) * wind_intensity, m.sin(wind_direction) * wind_intensity)
    angle = m.arccos((np.dot([fire_direction, vec.wind_direction]))/(module1*wind_intesity))
    return clamper(1 + m.cos(angle))

# sub-class the Engine and create your custom update function for each cell of the simulation
class MySim(GfxEngine):
  
    #
    # for each cell, your simulation logic goes here
    #  
    #  delta                - time elapsed between simulation step (ms)
    #  row                  - the row for the current cell 
    #  col                  - the column for the current cell
    #  valid_coordinates    - the surrounding, valid, coordinates for this cell [(row, col)...]
    #
    def update(self, delta, row, col, valid_coordinates):

        # the current cell
        cell = self.model.get_full_state(row, col) 
        if cell[0] == self.model.STATE_IGNITION:

            ### *** do your total probability calculation here *** ###
            veg_density = self.model.get_state_veg_density(row, col)
            veg_humidity = self.model.get_state_veg_humidity(row, col)

            prob_density = veg_density 
            prob_humidity = 1 - veg_humidity 
            probability_of_fire = prob_density * prob_humidity
           
            # in the event of ignition turning into fire change the current cell to fire 
            if random() <= probability_of_fire:
                self.set_state(row, col, self.model.STATE_FIRE, self.model.get_parameter_value("max_fire_time"))
        else:

            # for each of the valid surrounding cells 
            for other_row, other_col in valid_coordinates:

                # the other surrounding cell from the valid coordinate list
                other_cell = self.model.get_full_state(other_row, other_col) 
          
                # we only care about the surrounding cells if they are vegitation 
                # and they have not changed in any way 
                if other_cell[0] == self.model.STATE_VEGITATION and not self.model.is_modified(other_row, other_col):

                    ### *** do your total probability calculation here *** ###

                    # calculate the slope between the current cell and the other cell
                    slope = (self.model.get_height(other_row, other_col) - self.model.get_height(row, col)) / self.model.get_parameter_value("scale")
          
                    # calculate the final probability of fire spreading
                    
                    d_row = other_row - row
                    d_col = other_col - col
                    
                    theta = (m.acos(d_row) * 180) / m.pi
                    
                    print("d_row %d, d_col %d, theta %f, wind direction %f" % (d_row, d_col, theta, self.model.get_parameter_value("wind_direction")))
                    
                    prob_wind = 1 #fire_wind(self.model.get_parameter_value("wind_direction"))

                    prob_slope = 0.01 if slope < 0 else 1 
 
                    other_cell_veg_density = self.model.get_state_veg_density(other_row, other_col)

                    prob_density = other_cell_veg_density

                    #prob_humidity = 1

                    probability_of_fire_spread = prob_wind
                    # prob_density * prob_slope * prob_wind

                    # in the event of fire spread, change the other cell to an ignition
                    if random() <= probability_of_fire_spread:
                        self.set_state(other_row, other_col, self.model.STATE_IGNITION, self.model.get_parameter_value("max_ignition_time"))

