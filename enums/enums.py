from enum import Enum

class FillMethod(Enum):
    MEAN = 'mean'
    MEDIAN = 'median'
    MODE = 'mode'
    ZERO = 'zero'
    DROP = 'drop'

class OutlierMethod(Enum):
    ZSCORE = 'zscore'
    IQR = 'iqr'