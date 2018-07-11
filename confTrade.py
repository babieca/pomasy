# -*- coding: utf-8 -*-

import sys
from datetime import datetime

sys.path.append("..")

# custom
from pms.tickers import TickerSymbol
from pms.trade import Trade, TransactionType

class ConfigTrade:

    def __init__(self, trades):
        self.trades = trades


    def get_trades(self, n: int=0) -> [Trade]:
        '''
        :param n: tuple with trade details
        :return: list of Trades()
        '''
        
        n = len(self.trades)-1 if n==0 else n
        
        trades = []
        for trade_data in self.trades[0:n+1]:
            trade = self.from_tuple(trade_data)
            trades.append(trade)

        return trades


    def get_trade(self) -> Trade:
        return next(iter(self.get_trades(1)))


    def get_trades_for_stock(self, ticker_symbol: TickerSymbol,
                             n: int=0):
        n = len(self.trades)-1 if n==0 else n
        return [trade for trade in self.get_trades()
                if trade.ticker_symbol is ticker_symbol][:n+1]


    def get_trade_for_stock(self, ticker_symbol: TickerSymbol):
        return next(iter(self.get_trades_for_stock(ticker_symbol)))


    def from_tuple(self, trade_data: tuple) -> Trade:
        return Trade(ticker_symbol=trade_data[0],
                     timestamp=datetime.strptime(trade_data[1], '%Y-%m-%dT%H:%M:%S'),
                     quantity=trade_data[2],
                     price=trade_data[3],
                     trans_type=trade_data[4])
