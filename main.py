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
    
        
    

if __name__ == '__main__':
    historical = preprocess("SPY")
    historical = nMovingAverage(historical, 50)
    historical = nMovingAverage(historical, 200)
    historical["diff"] = historical["50-day SMA"] > historical["200-day SMA"]
    historical["diff-next"] = historical["diff"].shift(1)
    historical["golden-cross"] = ((historical["diff"] == True) & (historical["diff-next"] == False))
    historical["death-cross"] = ((historical["diff"] == False) & (historical["diff-next"] == True))

    test = historical[historical["golden-cross"] == True]
    print(test)
    
    # Get Rate of Change at each period
    historical["roc-25"] = nPriceRateOfChangeTotal(historical, 25)
    plt.plot(historical.index, historical["roc-25"])
    plt.title("Rate of Change n = 25 periods")
    plt.show()
    
    # Get a window of the Close prices
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.plot(getCloseWindow(historical, 3000, 150))
    ax2.plot(getROCWindow(historical, 3000, 150, 25))
    ax1.set_title('Stock Closing Prices')
    ax2.set_title('Rate of Change in Closing Prices')
    fig.savefig('fig.png')
    
    
    historical.to_csv("historical.csv")
    fig, ax = plt.subplots()
    plt.plot(historical.index, historical["Close"])
    plt.plot(historical["50-day SMA"], "r--", label="50-day SMA")
    plt.plot(historical["200-day SMA"], "b--", label="200-day SMA")
    plt.show()
