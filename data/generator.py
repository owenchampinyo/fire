import argparse 
import numpy as np 

parser = argparse.ArgumentParser()
parser.add_argument("-rows", type = int, required = True) 
parser.add_argument("-cols", type = int, required = True)
parser.add_argument("-shape", choices = ["slope", "dome", "fractal"],  required = True) 
parser.add_argument("-file",)

args = parser.parse_args()

data = np.zeros((args.rows, args.cols))

match args.shape:
    case "slope":
        for r in range(args.rows):
            for c in range(args.cols):
                data[(r, c)] = c

np.save(args.file, data)




