# region imports
from AlgorithmImports import *
import datetime
from datetime import timedelta
import os

# endregion

# cuando en terminal pones lean backtest buy-and-hold ejecuta dicha estrategia

# class MyOwnIndicator(args1, args2):
#     def __init__(self, args1, args2):
#         super().__init__()
#         # Initialize your indicator here

#     def update(self, time, value):
#         # Update your indicator with new data
#         pass

class CustomData(PythonData):
    def get_source(self, config: SubscriptionDataConfig, date: datetime, is_live: bool) -> SubscriptionDataSource:
        # Old:
        # source = "https://www.dropbox.com/s/8v6z949n25hyk9o/custom_weather_data.csv?dl=1"
        # return SubscriptionDataSource(source, SubscriptionTransportMedium.REMOTE_FILE)

        # New:
        # Replace custom_weather_data.csv with the path to your data file in the data directory
        source = os.path.join("futurosSP500/ES_full_1min_continuous_ratio_adjusted.txt")
        return SubscriptionDataSource(source, SubscriptionTransportMedium.LOCAL_FILE)
    

    def reader(self, config: SubscriptionDataConfig, line: str, date: datetime, is_live_mode: bool) -> BaseData:
            if not (line.strip() and line[0].isdigit()): return None

            # New Index object
            index = CustomData()
            index.symbol = config.symbol

            try:
                # Example File Format:
                # Date,       Open       High        Low       Close     Volume      Turnover
                # 2011-09-13  7792.9    7799.9     7722.65    7748.7    116534670    6107.78
                # Out data:
                # 2008-01-02 06:00:00,1368.85,1370.24,1368.62,1370.01,2317
                # 
                data = line.split(',')
                index.time = datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S")
                index.end_time = index.time + timedelta(min=1)
                index.value = data[4]
                index["Open"] = float(data[1])
                index["High"] = float(data[2])
                index["Low"] = float(data[3])
                index["Close"] = float(data[4])
                index.volume = int(data[5])
                
                self.Log(f"Parsed line: {line.strip()} -> Time: {index.time}, Open: {index['Open']}, High: {index['High']}, Low: {index['Low']}, Close: {index['Close']}, Volume: {index.volume}")
            except:
                self.Log(f"----- ERROR ------ Failed to parse line: {line.strip()}")

            return index


class Buyandhold(QCAlgorithm):

    def initialize(self):
        # Locally Lean installs free sample data, to download more data please visit https://www.quantconnect.com/docs/v2/lean-cli/datasets/downloading-data
        self.set_start_date(2009, 10, 7)  # Set Start Date
        self.set_end_date(2010, 10, 11)  # Set End Date
        self.set_cash(100000)  # Set Strategy Cash

        # Initialize our custom data
        # qb = QuantBook()

        self.Log("Initializing Custom Data")

        # Add the symbol
        self._symbol_SP_fut = self.add_data(CustomData, "SP_fut",  Resolution.MINUTE).symbol

        self._simplemovingaverage = SimpleMovingAverage(20)

    def on_data(self, data: Slice):
        """on_data event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        """
        # if not self.portfolio.invested:
        #     self.set_holdings("SPY", 1)
        #     self.debug("Purchased Stock")
        self.Log("he llegadp a on_data --------------------------------------------------------------------------")
        bar = data.bars.get(self._symbol_SP_fut)
            
        if bar:
            self._simplemovingaverage.update(bar.end_time, bar.close)

            if self._simplemovingaverage.is_ready:
                # The current value of self._simplemovingaverage is represented by self._simplemovingaverage.current.value
                self.plot("SimpleMovingAverage", "simplemovingaverage", self._simplemovingaverage.current.value)
                # Plot all attributes of self._simplemovingaverage
                self.plot("SimpleMovingAverage", "rolling_sum", self._simplemovingaverage.rolling_sum.current.value)

                if not self.portfolio.invested:
                    if bar.close > self._simplemovingaverage.current.value:
                        self.set_holdings("SPY", 1)
                        self.debug("Purchased Stock")
                else:
                    if bar.close < self._simplemovingaverage.current.value:
                        self.liquidate("SPY")
                        self.debug("Sold Stock")
