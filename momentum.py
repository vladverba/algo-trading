import yfinance as yf
import pandas as pd
import numpy as np


# calculate momentum
def calculate_momentum(data, period=1):
    """
    Calculate the momentum for each row in the DataFrame.

    Parameters:
    data (DataFrame): The DataFrame containing historical price data.
    period (int): The number of periods to look back for momentum calculation.

    Returns:
    DataFrame: A DataFrame with an additional column for momentum.
    """
    data["Momentum"] = data["Close"] - data["Close"].shift(period)
    return data


# add buy/sell/hold indicator
def add_buy_sell_hold_indicator(data):
    """
    Add buy, sell, and hold indicators based on momentum with thresholds.

    Parameters:
    data (DataFrame): The DataFrame containing historical price data with momentum.

    Returns:
    DataFrame: A DataFrame with an additional column for buy/sell/hold indicator.
    """

    threshold = 1

    data["Signal"] = np.where(
        data["Momentum"].isna(),
        None,
        np.where(
            data["Momentum"] > threshold,
            "Buy",
            np.where(data["Momentum"] < -threshold, "Sell", "Hold"),
        ),
    )
    return data


# backtest the strategy
def backtest(data, starting_capital=1000):

    current_value = starting_capital
    shares = 0

    for index, row in data.iterrows():
        if row["Signal"] == "Buy" and current_value > 0:
            shares_to_buy = current_value // row["Close"]
            shares += shares_to_buy
            current_value -= shares_to_buy * row["Close"]
        elif row["Signal"] == "Sell" and shares > 0:
            current_value += shares * row["Close"]
            shares = 0

    final_value = current_value + (shares * data.iloc[-1]["Close"])
    return final_value


if __name__ == "__main__":

    # Download historical data for a specific ticker
    ticker = "AAPL"
    data = yf.download(ticker, interval="1h", period="ytd")

    # flatten the dataframe
    data.columns = [col[0] for col in data.columns.values]

    # Calculate momentum with a default period of 1
    data_with_momentum = calculate_momentum(data)

    # Add buy/sell/hold indicator
    data_with_signals = add_buy_sell_hold_indicator(data_with_momentum)

    print(backtest(data_with_signals))
