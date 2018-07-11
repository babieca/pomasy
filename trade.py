# -*- coding: utf-8 -*-

import enum
from datetime import datetime

# custom modules
from .tickers import TickerSymbol

@enum.unique
class TransactionType(enum.Enum):

    """Indicator to buy or sell that accompanies each trade"""

    BL =  1     # Buy long
    SL = -1     # Sell long
    BC =  2     # Buy to cover
    SS = -2     # Sell short


class Trade:

    """A change of ownership of a collection of shares at a definite price per share"""

    def __init__(self,
                 trd_timestamp: datetime,
                 trd_ticker: TickerSymbol,
                 trd_type: TransactionType,
                 trd_qtty: int,
                 trd_px: float,
                 trd_ccy: str,
                 trd_lmt: float,
                 trd_status: str,
                 trd_brkr: str,
                 trd_type: list,
                 trd_TIF: list,
                 trd_cfd: bool,
                 trd_accounts: str):
        """
        :param timestamp: The moment when the transaction has taken place
        :param quantity: The amount of shares exchanged
        :param price: Price for each share
        :param trans_type: Indication to buy or sell
        """

        self.trd_timestamp = trd_timestamp
        self.trd_ticker = trd_ticker
        self.trd_type = trd_type

        if trd_qtty > 0:
            self.trd_quantity = trd_qtty
        else:
            msg = "The quantity of shares has to be positive."
            raise ValueError(msg)

        if trd_px >= 0.0:
            self.trd_px = trd_px
        else:
            msg = "The price per share can not be negative."
            raise ValueError(msg)

        self.trd_ccy = trd_ccy
        self.trd_lmt = trd_lmt
        self.trd_status = trd_status
        self.trd_brkr = trd_brkr
        self.trd_type = trd_type
        self.trd_TIF = trd_TIF
        self.trd_cfd = trd_cfd
        self.trd_accounts = trd_accounts

