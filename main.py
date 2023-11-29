from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

from MyStrategy import MyStrategy

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname= 'datas/orcl-1995-2014.txt',
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
