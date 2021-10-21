import cProfile
import os

import numpy as np

from pygef import Cpt

cwd = os.path.dirname(__file__)


def main():
    for _ in range(0, 1000):
        gef = Cpt("./pygef/test_files/example.gef")


if __name__ == "__main__":
    main()
