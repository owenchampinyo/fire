import numpy as np 
import util.math as m
from random import random, seed

# states 
#
# -1 - sea!
#  0 - nothing, rock!
#  1 - vegitation
#  2 - ignition 
#  3 - fire 
#  4 - burned

#
# this class holds the model data used by the sim engine
#
class Model:
    STATE_WATER = -1
    STATE_NOTHING = 0 
    STATE_VEGITATION = 1
    STATE_IGNITION = 2
    STATE_FIRE = 3
    STATE_BURNED = 4
 
    ATTRIBUTE_COUNT = 5

    IDX_STATE = 0
    IDX_TIME_TO_LIVE = 1
    IDX_TIME = 2
    IDX_VEG_DENSITY = 3
    IDX_VEG_HUMIDITY = 4

    def __init__(self, height_data, parameters):
        self.__rows = height_data.shape[0]
        self.__cols = height_data.shape[1]
        self.__height_data = height_data
        self.__parameters = parameters
        scale = self.get_parameter_value("scale")
        dx, dy = np.gradient(self.__height_data, scale, scale)
        self.__slope_data = np.degrees(np.arctan(np.hypot(dx, dy)))
        self.__max_height = np.max(self.__height_data)
        self.__min_height = np.min(self.__height_data, 
                                   where = np.greater(self.__height_data, 0), 
                                   initial = self.__max_height)
        self.__valid_range = m.valid_range(0, self.__rows, 0, self.__cols)

        print("dimensions   - rows %d, cols %d, scale %d" % (self.__rows, self.__cols, scale))
        print("height       - min %f, max %f" % (np.min(self.__height_data), np.max(self.__height_data)))
        print("model height - min %f, max %f" % (self.__min_height, self.__max_height))
        print("slope        - min %f, max %f" % (np.min(self.__slope_data), np.max(self.__slope_data)))

    #
    # initialise the model, take the base data (height) and derive other data
    #
    # 0 state, the state; nothing, fire etc.
    # 1 time to live, how long the state remains before transition
    # 2 time, the current time alive
    #
    # 3 vegitation density 
    # 4 vegitation humidity 
    #
    def init(self):
        seed(self.get_parameter_value("seed"))
        self.__modified = np.zeros((self.__rows, self.__cols))
        self.__state = np.zeros((self.__rows, self.__cols, self.ATTRIBUTE_COUNT))
        height_lerper = m.lerp(self.__min_height, self.__max_height)
        veg_density_decayer = m.decay(self.get_parameter_value("veg_density_decay"))
        veg_humidity_decayer = m.decay(self.get_parameter_value("veg_humidity_decay"))
        clamper = m.clamp(0, 1)
        for row in range(self.__rows):
            for col in range(self.__cols):
                coords = (row, col)
                height = self.__height_data[coords]
                if height <= 0:
                    self.__state[(row, col)] = [self.STATE_WATER, 0, 0, 0, 0]
                else:
                    height_lerp = height_lerper(height)
                    veg_density_decay = veg_density_decayer(height_lerp)
                    veg_density = clamper(veg_density_decay)
                    veg_humidity_decay = veg_humidity_decayer(height_lerp)
                    veg_humidity = clamper(veg_humidity_decay)
                    if random() < self.get_parameter_value("veg_probability") * veg_density:
                        self.__state[(row, col)] = [self.STATE_VEGITATION, 0, 0, veg_density, veg_humidity]
                    else:
                        self.__state[(row, col)] = [self.STATE_NOTHING, 0, 0, 0, 0]

    def get_parameters(self):
        return self.__parameters

    def get_parameter_title(self, name):
        return self.__parameters[name]["title"]

    def get_parameter_type(self, name):
        return self.__parameters[name]["type"]

    def get_parameter_value(self, name):
        return self.__parameters[name]["value"]

    def set_parameter_value(self, name, value):
        self.__parameters[name]["value"] = value

    def get_state(self, row, col):
        return self.__state[(row, col)][self.IDX_STATE]

    def set_state(self, row, col, state, time_to_live):
        self.__state[(row, col)][self.IDX_STATE] = state
        self.__state[(row, col)][self.IDX_TIME_TO_LIVE] = time_to_live
        self.__state[(row, col)][self.IDX_TIME] = 0

    def update_state_time(self, row, col, time):
        self.__state[(row, col)][self.IDX_TIME] = time

    def get_state_time_to_live(self, row, col):
        return self.__state[(row, col)][self.IDX_TIME_TO_LIVE]

    def get_state_time(self, row, col):
        return self.__state[(row, col)][self.IDX_TIME]

    def get_state_veg_density(self, row, col):
        return self.__state[(row, col)][self.IDX_VEG_DENSITY]

    def get_state_veg_humidity(self, row, col):
        return self.__state[(row, col)][self.IDX_VEG_HUMIDITY]

    def get_seed(self):
        return self.__seed

    def reset_modified(self):
        self.__modified.flat = 0

    def set_modified(self, row, col):
        self.__modified[(row, col)] = 1

    def is_modified(self, row, col):
        return self.__modified[(row, col)] == 1

    def get_full_state(self, row, col):
        return self.__state[(row, col)]

    def get_shape(self):
        return self.__height_data.shape

    def get_rows(self):
        return self.__rows

    def get_cols(self):
        return self.__cols

    def get_scale(self):
        return self.__scale

    def get_height(self, row, col):
        return self.__height_data[row, col]

    def get_min_height(self):
        return self.__min_height

    def get_max_height(self):
        return self.__max_height

    def get_slope(self, row, col):
        return self.__slope_data[row, col]

    def is_valid_range(self, row, col):
        return self.__valid_range(row, col)

    def get_valid_coordinates(self, row, col):
        return m.valid_coordinates(row, col, self.__valid_range)

