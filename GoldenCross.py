import backtrader as bt


class GoldenCross(bt.Strategy):
    params = (('fast', 50), ('slow', 200), ('order_percentage', 0.95), ('ticker', 'SPY'))

    def __init__(self):
        self.fast_moving_average = bt.indicators.SMA(period=self.p.fast)  #(self.data.close, period=self.p.fast, plotname=f'{self.p.fast} day MA')
        self.slow_moving_average = bt.indicators.SMA(period=self.p.slow)  #(self.data.close, period=self.p.slow, plotname=f'{self.p.slow} day MA')
        self.crossover = bt.indicators.CrossOver(self.p.fast,self.p.slow)

    def next(self):
        pass
