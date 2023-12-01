import math

import backtrader as bt

from GoldenCross import GoldenCross


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
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
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
        self.trail_percent = 0.05

    def next(self):
        score = 0
        indicators = []
        if not self.in_position:
            if self.fast_ma.sma[0] > self.slow_ma.sma[0] > self.really_slow_ma.sma[0]:
                if self.adx.adx[0] > 40:
                    indicators.append("Adx > 40 & triple cruce de medias")
                    score += 6
                if self.adx.adx[0] > 20:
                    indicators.append("Adx > 20 & triple cruce de medias")
                    score += 3
                # Buy Signal
                # self.in_position = True
            else:
                if self.fast_ma.sma > self.slow_ma.sma:
                    if self.adx.adx[0] > 40:
                        indicators.append("Adx > 40 & doble cruce de medias")
                        score += 4
                    if self.adx.adx[0] > 20:
                        indicators.append("Adx > 20 & triple cruce de medias")
                        score += 2
            if self.data0.close[0] > self.bollinger.mid[0] > self.data0.close[-1]:
                indicators.append("cruce al alza de la banda de bollinger")
                score += 4
            # if self.data0.close[-2] < self.bollinger.mid[0] and self.data.close[-3] < self.bollinger.mid[0]:
              #   score += 2
            if self.data0.close[0] > self.parabolic_sar:
                indicators.append("Parabolico marca tendencia alcista")
                score += 1
            if self.data0.close[-1] < self.parabolic_sar and self.data0.close[-2] < self.parabolic_sar:
                indicators.append("Cambio de tendencia bajista a alcista segun Parabolico")
                score += 4
            if self.adx.DIplus[0] > self.adx.DIminus[0] and self.adx.DIplus[1] < self.adx.DIminus[1]:
                if self.adx.adx[0] >= 20:
                    indicators.append("Adx >= 20 y +DI corta al alza por encima de -DI")
                    score += 5
                if self.adx.adx[0] >= 40:
                    indicators.append("Adx >= 40 y +DI corta al alza por encima de -DI")
                    score += 10
            if self.momentum[0] > 0 >= self.momentum[-1]:
                indicators.append("Momentum al alza")
                score += 4
            if self.data0.close[0] > self.data0.close[-1]:
                if self.rsi.rsi[-1] < 30 < self.rsi.rsi[0]:
                    indicators.append("RSI rompe la linea de sobre venta al alza")
                    score += 7
                if self.rsi.rsi[0] >= 50:
                    indicators.append("RSI marca tendencia al alza con relativamente buena fuerza")
                    score += 2
            if self.macd.macd[0] > 0 > self.macd.macd[-1]:
                indicators.append("MACD cruza la barrera del 0 al alza")
                score += 6
            if self.macd.macd[0] > self.macd.lines[0]:
                indicators.append("MACD corta al alza la linea de señal")
                score += 2
            print("score: {}".format(score))
            print(indicators)
            if score >= 6:
                buy_price = self.data0.close[0] if not math.isnan(self.data0.close[0]) else None
                self.order = self.buy(data=self.data0, price=buy_price, size=2,
                                      exectype=bt.Order.StopTrail,
                                      trailpercent=self.trail_percent, parent=self.sell(
                        price=buy_price,
                        exectype=bt.Order.Stop
                    ))

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
