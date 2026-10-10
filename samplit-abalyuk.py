import sys
import random

with open(sys.argv[1]) as f:
    for line in f:
        if random.random() < 0.01:
            print(line, end="")
