import backtrader as bt

from GoldenCross import GoldenCross


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
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast_length)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow_length)
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.p.rsi_length)
        self.in_position = False

    def next(self):
        self.log('sma: {}' .format(self.fast_ma.sma))
        if not self.in_position:
            if self.slow_ma > self.fast_ma and self.rsi < self.p.rsi_oversold:
                # Buy Signal
                self.buy(data=self.data, size=912)
                self.in_position = True
        else:
            if self.slow_ma < self.fast_ma or self.rsi > self.p.rsi_overbought:
                # Sell Signal
                self.sell(data=self.data, size=912)
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
