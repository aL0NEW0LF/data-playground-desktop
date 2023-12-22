from enum import Enum

class FillMethod(Enum):
    MEAN = 'mean'
    MEDIAN = 'median'
    MODE = 'mode'
    ZERO = 'zero'
    DROP = 'drop'
