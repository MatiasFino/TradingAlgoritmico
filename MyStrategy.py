import datetime
import math

import backtrader as bt


class MyStrategy(bt.Strategy):
    params = (
        ("fast_length", 30),
        ("slow_length", 50),
        ("really_slow_length", 100),
        ("rsi_length", 14),
        ("rsi_overbought", 70),
        ("rsi_oversold", 30),
        ("rsi_mid", 50),
        ("stop_loss", 0.02),
        ("take_profit", 0.05),
        ("start_date", datetime.datetime(2000, 1, 1)),
        ("end_date", datetime.datetime(2004, 12, 31)),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.order_status = False
        self.highest_price_so_far = 0
        self.order = None
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast_length)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow_length)
        self.really_slow_ma = bt.indicators.SMA(self.data.close, period=self.p.really_slow_length)
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.p.rsi_length)
        self.bollinger = bt.indicators.BollingerBands()
        self.parabolic_sar = bt.indicators.ParabolicSAR()
        self.adx = bt.indicators.AverageDirectionalMovementIndex()
        self.momentum = bt.indicators.MomentumOscillator()
        self.macd = bt.indicators.MACD()
        self.in_position = False
        self.stop_loss = 0.95
        self.order_size = 10000

    def next(self):
        score = 0
        indicators = []

        if not self.in_position:
            if self.fast_ma.sma[0] > self.slow_ma.sma[0] > self.really_slow_ma.sma[0] and (self.fast_ma.sma[-1]
                                                                                           < self.slow_ma.sma[-1] or
                                                                                           self.really_slow_ma.sma[-1] >
                                                                                           self.slow_ma.sma[-1]):
                if self.adx.adx[0] > 40:
                    indicators.append("Adx > 40 & triple moving average crossover")
                    score += 50
                if self.adx.adx[0] > 20:
                    indicators.append("Adx > 20 & triple moving average crossover")
                    score += 15

            else:
                if self.fast_ma.sma > self.slow_ma.sma and self.fast_ma.sma[-1] < self.slow_ma.sma[-1]:
                    if self.adx.adx[0] > 40:
                        indicators.append("Adx > 40 & dual moving average crossover")
                        score += 30
                    if self.adx.adx[0] > 20:
                        indicators.append("Adx > 20 & triple moving average crossover")
                        score += 5
            if self.data0.close[0] > self.bollinger.mid[0] > self.data0.close[-1]:
                indicators.append("Bollinger Band breakout to the upside")
                score += 10
            # if self.data0.close[-2] < self.bollinger.mid[0] and self.data.close[-3] < self.bollinger.mid[0]:
            #   score += 2
            if self.data0.close[0] > self.parabolic_sar:
                indicators.append("Parabolic SAR signals bullish trend")
                score += 5
            if self.data0.close[-1] < self.parabolic_sar and self.data0.close[-2] < self.parabolic_sar:
                indicators.append("Switch from bearish to bullish trend according to Parabolic")
                score += 25
            if self.adx.DIplus[0] > self.adx.DIminus[0] and self.adx.DIplus[-1] < self.adx.DIminus[-1]:
                if self.adx.adx[0] >= 20:
                    indicators.append("Adx >= 20 and +DI crosses above -DI")
                    score += 10
                if self.adx.adx[0] >= 40:
                    indicators.append("Adx >= 40 and +DI crosses above -DI")
                    score += 30
            if self.momentum[0] > 0 >= self.momentum[-1]:
                indicators.append("Bullish momentum")
                score += 10
            if self.data0.close[0] > self.data0.close[-1]:
                if self.rsi.rsi[-1] < 30 < self.rsi.rsi[0]:
                    indicators.append("RSI breaks out of oversold territory to the upside")
                    score += 20
                if self.rsi.rsi[0] >= 50:
                    indicators.append("RSI trends upward with relatively good strength")
                    score += 10
            if self.macd.macd[0] > 0 > self.macd.macd[-1]:
                indicators.append("MACD breaks through the 0 line to the upside")
                score += 25
            if self.macd.macd[0] > self.macd.lines[0]:
                indicators.append("MACD crosses to the upside over the signal line")
                score += 10
            print("score: {}".format(score))
            print(indicators)
            if score >= 20:

                if not self.in_position:  # and self.data0.datetime.datetime(0) < self.p.end_date - 2:
                    print("New hsf")
                    self.highest_price_so_far = self.data0.close[0]
                    print("Highest price so far {}".format(self.highest_price_so_far))
                    # Lógica para abrir una posición de compra
                    buy_price = self.data0.close[0] if not math.isnan(self.data0.close[0]) else None
                    self.order = self.buy(data=self.data0, price=buy_price, size=self.order_size)

                    # Calcular el precio de stop loss (venta) como porcentaje de la orden de compra

                    # Crear una orden de venta (stop loss) asociada a la orden de compra
                    # self.trail_order = self.sell(
                    #     data=self.data0,
                    #     price=trail_price,
                    #     parent=self.order,
                    #     exectype=bt.Order.Stop
                    # )

        if self.in_position:
            # if self.data0.datetime.datetime(0) == self.p.end_date - 1:
            # self.sell(size=self.order_size)
            if self.data0.close[0] > self.highest_price_so_far:
                self.highest_price_so_far = self.data0.close[0]
            print("Highest price so far in position {}".format(self.highest_price_so_far))
            print("Date {}".format(self.data0.datetime.datetime(0)))
            print("Actual price {}".format(self.data0.close[0]))
            print("{}% {}".format(self.stop_loss, self.highest_price_so_far * self.stop_loss))
            # Lógica para gestionar la posición existente
            # Aquí puedes agregar lógica para tomar beneficios, etc.

            # Ejemplo de cerrar la posición después de cierto número de días
            if self.data0.close[0] <= self.highest_price_so_far * self.stop_loss:
                self.log("Selling with stop loss at 5% less than highest price")
                self.sell(size=self.order_size)

    def notify_order(self, order):
        if order.status is order.Completed:
            if order.isbuy():
                self.log('BUY order COMPLETED with id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                                   order.executed.price))
            elif order.issell():
                self.log('SELL order COMPLETED with id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                                  order.executed.price))

        if order.status is order.Accepted:
            if order.isbuy():
                self.log('BUY order ACCEPTED with id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                                 order.created.price))
                self.in_position = True  # Establecer la posición como abierta
            elif order.issell():
                self.log('SELL order ACCEPTED with id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                                order.created.price))
                self.in_position = False
            self.cancel(order)

        if order.status is order.Submitted:
            if order.isbuy():
                self.log('BUY order SENT with id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                                order.created.price))
            elif order.issell():
                self.log('SELL order SENT with id: {} [{} @ ${}]'.format(order.ref, abs(order.size),
                                                                               order.created.price))
