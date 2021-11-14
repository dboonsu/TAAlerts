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

def nPriceRateOfChange(historical, n):
    # (ClosingPrice[p] - ClosingPrice[p-n])/ClosingPrice[p-n]
    # Verify n not greater than period
    if n > len(historical.Closing) - 1:
        raise IndexError("n periods exceeds the amount of data available")
    else:
        # historical.Closing[-1] is the most recent closing data
        return (historical.Closing[-1] - historical.Closing[-1 - n]) / historical.Closing[-1 - n]


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

    historical.to_csv("historical.csv")
    fig, ax = plt.subplots()
    plt.plot(historical.index, historical["Close"])
    plt.plot(historical["50-day SMA"], "r--", label="50-day SMA")
    plt.plot(historical["200-day SMA"], "b--", label="200-day SMA")
    plt.show()

