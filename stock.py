import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import yfinance as yf

from datetime import date, timedelta
import numpy as np
import matplotlib as mpl


class StockView():
    def __init__(self, stock_name):
        self.stock_name = stock_name

    def create_graph(self):
        start = date.today() - timedelta(600)
        end = date.today() + timedelta(2)
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')

        stock_chart = pd.DataFrame(yf.download(self.stock_name, start=start_str, end=end_str, multi_level_index= False)).rename(columns={'Close': 'Adj Close'})  

        moving_averages = [5, 20, 30, 60, 120]
        sma_data = pd.DataFrame()

        for window in moving_averages:
            sma_data[f'ma_{window}'] = stock_chart['Adj Close'].rolling(window=window).mean()

        ma_chart = stock_chart.copy()[['Adj Close']].join(sma_data)

        ma_chart["bull"] = np.where(
            ma_chart.iloc[:, 1:] > ma_chart.iloc[:, 2:].shift(1), 1, 0).all(axis=1)
        ma_chart["bear"] = np.where(
            ma_chart.iloc[:, 1:] < ma_chart.iloc[:, 2:].shift(1), -1, 0).all(axis=1)

        bull_marked = self.mark_periods(ma_chart, 'bull')
        bear_marked = self.mark_periods(ma_chart, 'bear')

        stock_chart_tail_60 = stock_chart.index[-60]
        stock_chart_tail_120 = stock_chart.index[-120]

        plt.figure(figsize=(40, 10))
        ax = plt.gca()
        ax.set_facecolor('#ffffff')

        self.plot_marked_periods(bull_marked, '#ffffd4')
        self.plot_marked_periods(bear_marked, '#6b8ba4')

        text_height = max(stock_chart['Adj Close']) * 0.618 + 40

        self.plot_ma_line(stock_chart, 'black', 5, 'stock price')
        for window in moving_averages:
            self.plot_ma_line(sma_data, self.get_color_for_window(window), window)

        plt.title(f'{self.stock_name} Performance')
        plt.ylabel('Price ($)')
        plt.xlabel('Date')
        plt.legend()
        fig_stock = plt.gcf()
        plt.grid()
        plt.show()
        fig_stock.savefig('static/stock_plot.png')

    def mark_periods(self, data, column):
        marked = data[data[column] == 1]
        marked['lag date'] = marked.index.shift(1)
        marked['date diff'] = (marked['lag date'] - marked.index).astype('timedelta64[h]') / 24
        marked['mark'] = np.where(marked['date diff'] < -5, 1, 0)
        marked_marked = marked[marked['mark'] == 1]
        start_dates = marked_marked['date'].tolist()
        end_dates = marked_marked['lag date'][1:].tolist()
        end_dates.append(marked.index[-1])
        assert len(start_dates) == len(end_dates)
        return start_dates, end_dates

    def plot_marked_periods(self, marked_periods, color):
        for start, end in zip(*marked_periods):
            plt.axvspan(start, end, facecolor=color)

    def plot_ma_line(self, data, color, window, label=None):
        plt.plot(data[f'ma_{window}'], color=color, linewidth=1, label=label)

    def get_color_for_window(self, window):
        colors = ['red', 'orange', 'green', 'blue', 'purple']
        return colors[window // 20]

    def save_plot_to_tmp(self):
        plot_file = os.path.join('/tmp', 'stock_plot.png')
        plt.savefig(plot_file)
        os.remove(plot_file)
