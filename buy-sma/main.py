# region imports
from AlgorithmImports import *
# endregion

class SmaStrategy(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2013, 10, 7)
        self.set_end_date(2013, 10, 11)
        self.set_cash(100000)

        self.symbol = self.add_equity("SPY", Resolution.MINUTE).symbol
        
        # SMA period
        self.sma_period = 20
        self.sma = self.sma(self.symbol, self.sma_period, Resolution.MINUTE)

        # Warm up to avoid empty indicator values
        self.set_warm_up(self.sma_period)

    def on_data(self, data: Slice):
        if self.is_warming_up:
            return

        if not data.contains_key(self.symbol):
            return

        price = data[self.symbol].close

        # Ensure SMA is ready
        if not self.sma.is_ready:
            return

        sma_value = self.sma.current.value

        # Buy condition
        if price > sma_value and not self.portfolio.invested:
            self.set_holdings(self.symbol, 1)
            self.debug(f"BUY @ {price} | SMA: {sma_value}")

        # Sell condition
        elif price < sma_value and self.portfolio.invested:
            self.liquidate(self.symbol)
            self.debug(f"SELL @ {price} | SMA: {sma_value}")