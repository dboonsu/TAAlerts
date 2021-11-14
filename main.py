import datetime

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def preprocess(name):
    temp = yf.Ticker(name)
    historical = pd.DataFrame(temp.history(period="max"))
    historical = historical.drop(columns=["Dividends", "Stock Splits"])
    return historical

def nMovingAverage(historical, n):
    historical[str(n) + "-day SMA"] = historical.Close.rolling(n, min_periods=n).mean()
    return historical

def relativeStrengthIndex(historical):
    dayOne = historical.index[15]
    historical["Close-Prev"] = historical["Close"].shift(1)
    historical["Change"] = historical["Close"] - historical["Close-Prev"]
    historical["Gain"] = (historical["Change"].where(historical["Change"] >= 0))
    historical["Loss"] = (historical["Change"].where(historical["Change"] < 0) * -1)
    historical.fillna(0, inplace=True)
    historical["AverageGain"] = historical.Gain.rolling(14).mean()
    historical["AverageLoss"] = historical.Loss.rolling(14).mean()
    temp = dayOne
    for idx, val in historical.iterrows():
        if (idx < dayOne):
            continue
        historical.loc[idx, "AverageGain"] = round((((historical.loc[temp, "AverageGain"] * 13) + historical.loc[idx, "Gain"])/14), 2)
        historical.loc[idx, "AverageLoss"] = round((((historical.loc[temp, "AverageLoss"] * 13) + historical.loc[idx, "Loss"])/14), 2)
        temp = idx
    historical["RS"] = historical["AverageGain"] / historical["AverageLoss"]
    historical["RSI"] = 100 - (100 / (1 + historical["RS"]))
    return historical

# def dateRange(start, end, historical, temp):
#     for i in range((end-start).days):
#     return temp
#
# def showGoldenCross(historical, goldenCross):
#     fig, ax = plt.subplots()
#     temp = pd.DataFrame
#     for idx, val in goldenCross.iterrows():
#         plt.plot()
#         temp = dateRange(idx - datetime.timedelta(25), idx + datetime.timedelta(25), historical, temp)
#     plt.plot(historical.index)

def nPriceRateOfChange(historical, p, n):
    # (ClosingPrice[p] - ClosingPrice[p-n])/ClosingPrice[p-n]
    # p is the most recent period
    # n is the number of periods back you want to consider
    
    # Verify n not greater than period
    # That is, find the index of the pervious period
    # use 0 for early periods
    prev_period = 0 if p < n else p - n

    return 100 * (historical.Close[p] - historical.Close[prev_period]) / historical.Close[prev_period]

def nPriceRateOfChangeTotal(historical, n):
    roc = []
    for p in range(len(historical.Close)):
        roc.append(nPriceRateOfChange(historical, p, n))
    return roc
        
# Get a window (pos +- window) of the Close data
def getCloseWindow(historical, pos, window):
    begin = pos - window if window < pos else 0
    end = pos + window if pos + window < len(historical.Close) else len(historical.Close)
    return historical.Close[begin:end]
    
def getROCWindow(historical, pos, window, n):
    str_name = 'roc-{}'.format(n)
    begin = pos - window if window < pos else 0
    end = pos + window if pos + window < len(historical[str_name]) else len(historical[str_name])
    return historical[str_name][begin:end]
    

def getRSIWindow(historical, pos, window):
    begin = pos - window if window < pos else 0
    end = pos + window if pos + window < len(historical["RSI"]) else len(historical["RSI"])
    return historical["RSI"][begin:end]


if __name__ == '__main__':
    historical = preprocess("SPY")
    relativeStrengthIndex(historical)
    historical = nMovingAverage(historical, 50)
    historical = nMovingAverage(historical, 200)
    historical["cross"] = historical["50-day SMA"] > historical["200-day SMA"]
    historical["cross-next"] = historical["cross"].shift(1)
    historical["golden-cross"] = ((historical["cross"] == True) & (historical["cross-next"] == False))
    historical["death-cross"] = ((historical["cross"] == False) & (historical["cross-next"] == True))

    goldenCross = historical[historical["golden-cross"] == True]
    deathCross = historical[historical["death-cross"] == True]
    # print(goldenCross)
    # temp = datetime.date(year=1993, day=11, month=11)
    # print(goldenCross.loc["1993-11-11", "Close"])
    # showGoldenCross(historical, goldenCross)

    test = historical[historical["golden-cross"] == True]
    print(test)
    
    # Get Rate of Change at each period
    historical["roc-25"] = nPriceRateOfChangeTotal(historical, 25)
    plt.plot(historical.index, historical["roc-25"])
    plt.title("Rate of Change n = 25 periods")
    #plt.show()
    
    # Show the RoC against the closing prices
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.plot(getCloseWindow(historical, 3000, 150))
    ax2.plot(getROCWindow(historical, 3000, 150, 25))
    ax1.set_title('Stock Closing Prices')
    ax2.set_title('Rate of Change in Closing Prices')
    fig.savefig('roc.png')
    
    
    # Show the RSI against the closing prices
    fig2, (axA, axB) = plt.subplots(2, 1, sharex=True)
    axA.plot(getCloseWindow(historical, 3000, 150))
    axA.set_title('Stock Closing Prices')
    axB.plot(getRSIWindow(historical, 3000, 150))
    axB.axhline(y=30, color='r', linestyle='-')
    axB.axhline(y=70, color='r', linestyle='-')
    axB.set_ylim([0, 100])
    axB.set_title('Relative Strength Index')
    fig2.savefig('rsi.png')
    
    historical.to_csv("historical.csv")
    fig, ax = plt.subplots()
    plt.plot(historical.index, historical["Close"])
    plt.plot(historical["50-day SMA"], "r--", label="50-day SMA")
    plt.plot(historical["200-day SMA"], "b--", label="200-day SMA")
    #plt.show()
    
    fig, ax = plt.subplots()
    plt.plot(historical.index, historical["RSI"])
    #plt.show()
