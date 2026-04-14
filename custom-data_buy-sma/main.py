# Imports
from AlgorithmImports import *
from datetime import datetime
from datetime import timedelta
import os


class SmaStrategy(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2009, 10, 7)
        self.set_end_date(2010, 10, 11)
        self.set_cash(100000)

        self.symbol = self.add_data(SPFut, "SPFut", Resolution.MINUTE).symbol
        
        # SMA period
        self.sma_period = 8*60*30  # 30 trading days of 8 hours each
        self.sma = SimpleMovingAverage(self.sma_period)

        # Warm up to avoid empty indicator values
        self.set_warm_up(self.sma_period)

        # Info
        self.debug("Algorithm initialized")

        self.debug("Global data folder: " + Globals.data_folder)

    def on_data(self, data: Slice):
        if self.is_warming_up:
            return

        if not data.contains_key(self.symbol):
            return

        price = data[self.symbol].close

        self.sma.update(self.time, price)

        # Ensure SMA is ready
        if not self.sma.is_ready:
            return

        sma_value = self.sma.current.value

        self.plot("SMA Chart", "Price", price)
        self.plot("SMA Chart", "SMA", sma_value)

        # Buy condition
        if price > sma_value and not self.portfolio.invested:
            self.set_holdings(self.symbol, 1)
            self.debug(f"BUY @ {price} | SMA: {sma_value}")

        # Sell condition
        elif price < sma_value and self.portfolio.invested:
            self.liquidate(self.symbol)
            self.debug(f"SELL @ {price} | SMA: {sma_value}")


class SPFut(PythonData):
    '''SP500 Futures Custom Data Class'''
    def get_source(self, config, date, is_live_mode):
        return SubscriptionDataSource(os.path.join(Globals.data_folder, "custom", "ES_full_1min_continuous_ratio_adjusted.txt"), SubscriptionTransportMedium.LOCAL_FILE, FileFormat.CSV)

    def reader(self, config, line, date, is_live_mode):
        if not (line.strip() and line[0].isdigit()): return None

        # New Nifty object
        index = SPFut()
        index.symbol = config.symbol

        try:
            # Example File Format:
            # Date,       Open       High        Low       Close     Volume      Turnover
            # 2011-09-13  7792.9    7799.9     7722.65    7748.7    116534670    6107.78
            # Our data
            # 2008-01-02 06:00:00,1368.85,1370.24,1368.62,1370.01,2317
            data = line.split(',')
            index.time = datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S")
            index.end_time = index.time + timedelta(minutes=1)
            index.value = float(data[4])
            index["Open"] = float(data[1])
            index["High"] = float(data[2])
            index["Low"] = float(data[3])
            index["Close"] = float(index.value)
            index.volume = int(data[5])
        except ValueError:
            return None

        return index