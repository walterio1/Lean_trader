# Imports
from AlgorithmImports import *
from datetime import datetime
from datetime import timedelta
import os
import gc
import sys


class SmaStrategy(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2009, 10, 7)
        self.set_end_date(2010, 10, 11)
        self.set_cash(100000)

        # Local variables
        self.state = False

        # Add symbols
        self.symbol_SPFut = self.add_data(SPFut, "SPFut", Resolution.MINUTE).symbol
        self.symbol_VIXSlope = self.add_data(VIXSlope, "VIXSlope", Resolution.DAILY).symbol
        
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

        if data.contains_key(self.symbol_VIXSlope):
            # Compute state
            self.state = data[self.symbol_VIXSlope].open > data[self.symbol_VIXSlope].close
            self.plot("SMA Chart", "VIX Slope - Value 1", data[self.symbol_VIXSlope].open)
            self.plot("SMA Chart", "VIX Slope - Value 2", data[self.symbol_VIXSlope].close)
            self.plot("SMA Chart", "VIX Slope - State", int(self.state))


        if data.contains_key(self.symbol_SPFut):
            price = data[self.symbol_SPFut].close

            self.sma.update(self.time, price)

            # Ensure SMA is ready
            if not self.sma.is_ready:
                return

            sma_value = self.sma.current.value

            self.plot("SMA Chart", "Price", price)
            self.plot("SMA Chart", "SMA", sma_value)

            # Buy condition
            if price > sma_value and not self.portfolio.invested:
                self.set_holdings(self.symbol_SPFut, 1)
                self.debug(f"BUY @ {price} | SMA: {sma_value}")

            # Sell condition
            elif price < sma_value and self.portfolio.invested:
                self.liquidate(self.symbol_SPFut)
                self.debug(f"SELL @ {price} | SMA: {sma_value}")

    def on_end_of_algorithm(self):
        # Explicit cleanup to prevent shutdown timeout
        self.sma = None
        self.symbol_SPFut = None
        self.symbol_VIXSlope = None
        gc.collect()
        sys.stdout.flush()
        sys.stderr.flush()


class SPFut(PythonData):
    '''SP500 Futures Custom Data Class'''
    
    def get_source(self, config, date, is_live_mode):
        return SubscriptionDataSource(os.path.join(Globals.data_folder, "custom", "ES_full_1min_continuous_ratio_adjusted.txt"), SubscriptionTransportMedium.LOCAL_FILE, FileFormat.CSV)

    def reader(self, config, line, date, is_live_mode):
        if not (line.strip() and line[0].isdigit()): 
            return None

        index = SPFut()
        index.symbol = config.symbol

        try:
            data = line.split(',')
            # Use fast datetime parsing
            dt_str = data[0]
            year = int(dt_str[:4])
            month = int(dt_str[5:7])
            day = int(dt_str[8:10])
            hour = int(dt_str[11:13])
            minute = int(dt_str[14:16])
            second = int(dt_str[17:19])
            
            index.time = datetime(year, month, day, hour, minute, second)
            index.end_time = index.time + timedelta(minutes=1)
            index.value = float(data[4])
            index["Open"] = float(data[1])
            index["High"] = float(data[2])
            index["Low"] = float(data[3])
            index["Close"] = float(index.value)
            index.volume = int(data[5])
        except (ValueError, IndexError):
            return None

        return index
    

class VIXSlope(PythonData):
    '''VIX SLope Custom Data Class'''
    
    def get_source(self, config, date, is_live_mode):
        return SubscriptionDataSource(os.path.join(Globals.data_folder, "custom", "preu123.csv"), SubscriptionTransportMedium.LOCAL_FILE, FileFormat.CSV)

    def reader(self, config, line, date, is_live_mode):
        if not (line.strip() and line[0].isdigit()): 
            return None

        index = VIXSlope()
        index.symbol = config.symbol

        try:
            data = line.split(',')
            # Use fast datetime parsing
            dt_str = data[0]
            year = int(dt_str[:4])
            month = int(dt_str[5:7])
            day = int(dt_str[8:10])
            
            index.time = datetime(year, month, day)
            index.end_time = index.time + timedelta(days=1)
            index["Open"] = float(data[1])
            index["Close"] = float(data[2])
        except (ValueError, IndexError):
            return None

        return index