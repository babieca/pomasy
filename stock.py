# -*- coding: utf-8 -*-

import abc

from datetime import datetime, timedelta

# custom modules
from pms.tickers import TickerSymbol
from pms.trade import Trade

class Stock(abc.ABC):

    """A publicly traded stock

    This is an abstract class that includes the common interface that both common
    and preferred stocks share.

    .. note:: The class variable Stock.price_time_interval serves as a configuration value
        to define the length of the time interval that is significant to calculate the VWAP
        (Volume Weighted Stock Price) in the pre-defined period (5 minutes default).
    """

    price_time_interval = timedelta(minutes=5)

    def __init__(self, ticker_symbol: TickerSymbol, par_value: float):
        """
        :param ticker_symbol: The ticker_symbol that identifies this stock
        :param par_value: The face value per share for this stock
        .. note:: This initializer also creates the instance variable self.trades,
            which is to hold a list of recorded instances of Trade.
        """
        self.ticker_symbol = ticker_symbol
        self.par_value = par_value

        self.trades = []

    def record_trade(self, trade: Trade):
        """Records a trade for this stock.
        :param trade: The trade to be recorded
        :raise TypeError:
        :raise ValueError:
        """
        if not isinstance(trade, Trade):
            msg = "Argument trade={trade} should be of type Trade.".format(trade=trade)
            raise TypeError(msg)
        elif self.ticker_symbol is not trade.ticker_symbol:
            msg = "Argument trade={trade} does not belong to this stock.".format(trade=trade)
            raise ValueError(msg)
        else:
            self.trades.append(trade)

    @property
    @abc.abstractmethod
    def dividend(self) -> float:
        """
        :return: A ratio that represents the dividend for this stock
        """
        pass

    @property
    def ticker_price(self) -> float:
        """
        :return: The price per share for the last recorded trade for this stock
        :raise AttributeError:
        .. note:: We don't know if the trades will be registered in chronological order.
            That is why self.trades is explicitly sorted.
        """
        if len(self.trades) > 0:
            by_timestamp = sorted(self.trades,
                                  key=lambda trade: trade.timestamp,
                                  reverse=True)
            return by_timestamp[0].price
        else:
            msg = "The last ticker price is not yet available."
            raise AttributeError(msg)

    @property
    def dividend_yield(self) -> float:
        return self.dividend / self.ticker_price

    @property
    def price_dividend_ratio(self) -> float:
        """
        :return: The P/E ratio for this stock
        """
        if self.dividend != 0:
            return self.ticker_price / self.dividend
        else:
            return 0

    def vwap(self, current_time: datetime=datetime.now()) -> float:
        """
        :param current_time: The point of time defined as the current one.
        :return: The average price per share (VWAP) based on trades recorded in the 
            last Stock.price_time_interval. None if there are 0 trades that satisfy
            this condition.
        .. note:: Though lean, the way in which selected_trades obtained may be
            unnecessarily costly, since it traverses all recorded trades and it may
            be possible to have them already ordered by trade.timestamp.
        .. note:: The existence of the current_time parameter avoids the inner user
            of datetime.now, thus keeping referential transparency and moving state out.
        """
        selected_trades = [trade for trade in self.trades
                              if trade.timestamp >= current_time - self.price_time_interval]

        if len(selected_trades) > 0:
            pxvol = shares = 0
            for trade in selected_trades:
                pxvol= pxvol + (trade.price * trade.quantity)
                shares = shares + trade.quantity
            return 0 if shares==0 else (pxvol / shares)
        else:
            return 0


class CommonStock(Stock):

    """A common stock"""

    def __init__(self,
                 ticker_symbol: TickerSymbol,
                 par_value: float,
                 last_dividend: float):
        """
        :param last_dividend: An absolute value that indicates the last dividend
            per share for this stock.
        """

        super().__init__(ticker_symbol, par_value)
        self.last_dividend = last_dividend

    @property
    def dividend(self):
        return self.last_dividend


class PreferredStock(Stock):

    """A preferred stock"""

    def __init__(self,
                 ticker_symbol: TickerSymbol,
                 par_value: float,
                 fixed_dividend: float):
        """
        :param fixed_dividend: A decimal number that expresses the fixed dividend
            as a ratio of the face value of each share.
        """

        super().__init__(ticker_symbol, par_value)
        self.fixed_dividend = fixed_dividend

    @property
    def dividend(self):
        return self.fixed_dividend * self.par_value