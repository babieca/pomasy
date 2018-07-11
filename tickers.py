# -*- coding: utf-8 -*-

import enum

@enum.unique
class TickerSymbol(enum.Enum):

    """Unique identifier for one of the traded stocks"""

    TEA = 1
    POP = 2
    ALE = 3
    GIN = 4
    JOE = 5