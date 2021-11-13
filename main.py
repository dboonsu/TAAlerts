import yfinance as yf
import pandas as pd
def preprocess(name):
    temp = yf.Ticker(name)
    historical = pd.DataFrame(temp.history(period="max"))
    historical = historical.drop(columns=["Dividends", "Stock Splits"])
    historical.to_csv("historical.csv")

if __name__ == '__main__':
    preprocess("SPY")