# -*- coding: utf-8 -*-
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
    start.strftime('%Y-%m-%d')

    end = date.today() + timedelta(2)
    end.strftime('%Y-%m-%d')

    stock_chart = pd.DataFrame(yf.download(self.stock_name, start=start,
      end=end, multi_level_index= False)).rename(columns={'Close': 'Adj Close'})                    # CALL THE FUNCTION
    

    sma_5 = pd.DataFrame()
    sma_5['Adj_Close_Price'] = stock_chart['Adj Close'].rolling(window = 5).mean()
    sma_20 = pd.DataFrame()
    sma_20['Adj_Close_Price'] = stock_chart['Adj Close'].rolling(window = 20).mean()
    sma_30 = pd.DataFrame()
    sma_30['Adj_Close_Price'] = stock_chart['Adj Close'].rolling(window = 30).mean()
    sma_60 = pd.DataFrame()
    sma_60['Adj_Close_Price'] = stock_chart['Adj Close'].rolling(window = 60).mean()
    sma_120 = pd.DataFrame()
    sma_120['Adj_Close_Price'] = stock_chart['Adj Close'].rolling(window = 120).mean()


    ma_chart = stock_chart.copy()[['Adj Close']]
    ma_chart['ma_5'] = sma_5['Adj_Close_Price']
    ma_chart['ma_20'] = sma_20['Adj_Close_Price']
    ma_chart['ma_30'] = sma_30['Adj_Close_Price']
    ma_chart['ma_60'] = sma_60['Adj_Close_Price']
    ma_chart['ma_120'] = sma_120['Adj_Close_Price']
    ma_chart = ma_chart.iloc[120:,:]

    ma_chart["bull"] =  np.where(((ma_chart.ma_5 > ma_chart.ma_20) \
                                                  & (ma_chart.ma_20 > ma_chart.ma_30) \
                                                  & (ma_chart.ma_30 > ma_chart.ma_60) \
                                                  & (ma_chart.ma_60 > ma_chart.ma_120) ) ,1, 0)
#df['c2'] = np.where(df.c1 == 8,'X', df.c3)

    ma_chart["bear"] =  np.where(((ma_chart.ma_5 < ma_chart.ma_20) \
                                                  & (ma_chart.ma_20 < ma_chart.ma_30) \
                                                  & (ma_chart.ma_30 < ma_chart.ma_60) \
                                                  & (ma_chart.ma_60 < ma_chart.ma_120) ) ,-1, 0)


    bull = ma_chart[ma_chart['bull'] == 1]
    bull['date'] = bull.index
    bull['lag date'] = bull['date'].shift(1)
    bull['date diff'] = bull['lag date'] - bull['date']
    bull['date diff'] = pd.to_numeric(bull['date diff'])
    bull['date diff'] = bull['date diff'] / (3600000000000*24)
    bull['mark'] = np.where(bull['date diff'] < -5, 1, 0)
    mark = bull[bull['mark'] == 1]
    bull_start_dates = []
    if len(mark) > 0:
      bull_start_dates = mark['date'].tolist()
      bull_end_dates = mark['lag date'][1:].tolist()
      bull_end_dates.append(bull.iloc[-1,-4])
      assert len(bull_start_dates) == len(bull_end_dates)

    bear = ma_chart[ma_chart['bear'] == -1]
    bear['date'] = bear.index
    bear['lag date'] = bear['date'].shift(1)
    bear['date diff'] = bear['lag date'] - bear['date']
    bear['date diff'] = pd.to_numeric(bear['date diff'])
    bear['date diff'] = bear['date diff'] / (3600000000000*24)
    bear['mark'] = np.where(bear['date diff'] < -5, 1, 0)
    mark = bear[bear['mark'] == 1]
    bear_start_dates = []
    if len(mark) > 0:
      bear_start_dates = mark['date'].tolist()
      bear_end_dates = mark['lag date'][1:].tolist()
      bear_end_dates.append(bear.iloc[-1,-4])
      assert len(bear_start_dates) == len(bear_end_dates)

    stock_chart.index[len(stock_chart)-60]


    f = plt.figure()
    f.set_figwidth(40)
    f.set_figheight(10)
    ax = plt.gca()
    ax.set_facecolor('#ffffff')


    if len(bull_start_dates) > 0 :
      for i in range(len(bull_start_dates)):
        plt.axvspan(bull_start_dates[i], bull_end_dates[i], facecolor='#ffffd4')
    if len(bear_start_dates) > 0 :
      for i in range(len(bear_start_dates)):
        plt.axvspan(bear_start_dates[i], bear_end_dates[i], facecolor='#6b8ba4')

    past_days_60 = stock_chart.index[len(stock_chart)-60]
    past_days_120 = stock_chart.index[len(stock_chart)-120]


    text_height = max(stock_chart['Adj Close'])*0.618 + 40

    plt.plot(stock_chart['Adj Close'],color='black', linewidth=5, label = "stock price")

    plt.plot(sma_5, color='red', linewidth=1, label = "5 days MA")
    plt.plot(sma_20, color='orange', linewidth=1, label = "20 days MA")
    plt.plot(sma_30, color='green', linewidth=1, label = "30 days MA")
    plt.plot(sma_60, color='blue', linewidth=1, label = "60 days MA")
    plt.plot(sma_120, color='purple', linewidth=1, label = "120 days MA")
    plt.title(f'{self.stock_name} Performance')
    plt.ylabel('Price ($)')
    plt.xlabel('Date')
    plt.legend()
    fig_stock = plt.gcf()
    plt.grid()
    plt.show()
    f2 = plt.figure()
    f2.set_figwidth(40)
    f2.set_figheight(5)
    ax2 = plt.gca()
    if len(bull_start_dates) > 0 :
      for i in range(len(bull_start_dates)):
        plt.axvspan(bull_start_dates[i], bull_end_dates[i], facecolor='#ffffd4')
    if len(bear_start_dates) > 0 :
      for i in range(len(bear_start_dates)):
        plt.axvspan(bear_start_dates[i], bear_end_dates[i], facecolor='#6b8ba4')

    plt.bar(stock_chart.index,stock_chart['Volume'], color = "orange")
    plt.grid()
    plt.ylabel('Volume in 100 million')

    plt.show()
    # Save the first plot as an image
    fig_stock.savefig('static/stock_plot.png')
    print(1)
    # Save the second plot as an image
    #f2.savefig('static/volume_plot.png')
    #print(2)
    plt.close(fig_stock)
    #plt.close(f2)
    #fig_stock.savefig(f'{stock}_chart.png')
    #return fig_stock


  
  def save_plot_to_tmp(self):
      # Save the plot image to the temporary file system
      plot_file = os.path.join('/tmp', 'stock_plot.png')
      plt.savefig(plot_file)

      os.remove(plot_file)
