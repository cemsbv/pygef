import cProfile
import os

import numpy as np
from pygef import ParseGEF

cwd = os.path.dirname(__file__)


def main():
    for _ in range(0, 1000):
        gef = ParseGEF("pygef/files/example.gef")


if __name__ == "__main__":
    main()
