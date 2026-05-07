from enum import Enum

class VialColour(Enum):
    YELLOW = 1,
    RED = 2,
    GREEN = 3,
    
class VialState(Enum):
    PRESENT = 0
    EMPTY = 1
    UNKNOWN = 2

class SubtractionMethod(Enum):
    KNN = 1
    MOG2 = 2