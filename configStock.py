# -*- coding: utf-8 -*-

import sys
from datetime import datetime

sys.path.append("..")

# custom
from pms.tickers import TickerSymbol
from pms.stock import Stock, CommonStock, PreferredStock

class ConfigStock:
    
    def __init__(self, stocks):
        self.STOCKS = stocks
        

    def get_stocks(self, n: int=0) -> [Stock]:
        """
        :param n: tuple with stocks details
        :return: list of CommonStocks() / PreferredStocks()
        :raise ValueError:
        """
        n = len(self.STOCKS)-1 if n==0 else n
        # empty list that will contain all the stocks
        stocks = []
        
        # loop over all the stocks from the input file
        for stock_data in self.STOCKS[0:n+1]:

            ticker_symbol = TickerSymbol(stock_data[0])
            par_value = stock_data[4]
            cls = stock_data[1]

            ''' Check if stocks is common/preferred.
            Otherwise, rise an error
            '''
            if cls is CommonStock:
                dividend = stock_data[2]
            elif cls is PreferredStock:
                dividend = stock_data[3]
            else:
                raise ValueError()

            # create the new stock (common/preferred)
            stock = cls(ticker_symbol, par_value, dividend)
            
            # append the new stock to the stack
            stocks.append(stock)

        return stocks


    def get_stock(self) -> Stock:
        return next(iter(self.get_stocks(1)))


    def get_stock_by_ticker_symbol(self, ticker_symbol: TickerSymbol):
        return next(stock for stock in self.get_stocks()
                    if stock.ticker_symbol is ticker_symbol)


    def get_zero_dividend_stock(self) -> Stock:
        return next(stock for stock in self.get_stocks()
                    if stock.dividend == 0)


    def get_common_stock(self) -> CommonStock:
        return next(stock for stock in self.get_stocks()
                    if isinstance(stock, CommonStock))


    def get_preferred_stock(self) -> PreferredStock:
        return next(stock for stock in self.get_stocks()
                    if isinstance(stock, PreferredStock))
