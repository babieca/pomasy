# -*- coding: utf-8 -*-

import operator
from datetime import datetime
from functools import reduce

# custom modules
from .trade import Trade
from .stock import Stock

class GlobalBeverageCorporationExchange:

    """The whole exchange where the trades take place"""

    def __init__(self, stocks: [Stock]):
        """
        :param stocks: The stocks traded at this exchange.
        :raise ValueError:
        """
        if len(stocks) > 0:
            self.stocks = stocks
        else:
            msg = "Argument stocks={stocks} should be a non empty sequence.".format(stocks=stocks)
            raise ValueError(msg)

    def record_trade(self, trade: Trade):
        """Records a trade for the proper stock.
        :param trade: The trade to record.
        """
        stock = next(stock for stock in self.stocks
                     if stock.ticker_symbol is trade.ticker_symbol)
        stock.record_trade(trade)

    def all_share_index(self, current_time: datetime=datetime.now()) -> float:
        """
        :param current_time: The point of time for which we want to obtain the index.
        :return: The geometric mean of all stock prices. Returns 0 if any of them is None.
        """
        n = len(self.stocks)
        stock_vwap = [stock.vwap(current_time) for stock in self.stocks]

        if None in stock_vwap: return 0

        product = reduce(operator.mul, stock_vwap, 1)
        return product**(1/n)