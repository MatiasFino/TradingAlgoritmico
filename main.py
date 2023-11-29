from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


class MyStrategy(bt.Strategy):
    params = (
        ("fast_length", 10),
        ("slow_length", 30),
        ("rsi_length", 14),
        ("rsi_overbought", 70),
        ("rsi_oversold", 30),
        ("rsi_mid", 50),
        ("stop_loss", 0.02),
        ("take_profit", 0.05),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.fast_length)
        self.slow_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.slow_length)
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.rsi_length)
        self.in_position = False

    def next(self):
        if not self.in_position:
            if self.slow_ma > self.fast_ma and self.rsi < self.params.rsi_oversold:
                # Buy Signal
                self.buy()
                self.in_position = True
        else:
            if self.slow_ma < self.fast_ma or self.rsi > self.params.rsi_overbought:
                # Sell Signal
                self.sell()
                self.in_position = False

    def notify_order(self, order):
        if order.status is order.Completed:
            if order.isbuy():
                self.log('Se completo la orden COMPRA de id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                                   order.executed.price))
            elif order.issell():
                self.log('Se completo la orden VENTA de id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                                  order.executed.price))

        if order.status is order.Accepted:
            if order.isbuy():
                self.log('Se acepto la orden COMPRA de id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                                 order.created.price))
            elif order.issell():
                self.log('Se acepto la orden VENTA de id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                                order.created.price))
            self.cancel(order)

        if order.status is order.Submitted:
            if order.isbuy():
                self.log('Se envio la orden COMPRA de id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                                order.created.price))
            elif order.issell():
                self.log('Se envio la orden VENTA de id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                               order.created.price))


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'datas/orcl-1995-2014.txt')

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2000, 1, 1),
        # Do not pass values after this date
        todate=datetime.datetime(2000, 12, 31),
        reverse=False,
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.addstrategy(MyStrategy)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
