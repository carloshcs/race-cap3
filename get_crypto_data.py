import requests
import pandas as pd
import time

# File path for storing data
excel_file = "crypto_market_cap_history.xlsx"

# CoinGecko API endpoints
COINS_MARKET_ENDPOINT = "https://api.coingecko.com/api/v3/coins/markets"
COIN_MARKET_CHART_ENDPOINT = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"

# List of stablecoins to exclude
EXCLUDED_STABLECOINS = {"tether", "usd-coin", "paxos-standard", "binance-usd", "gemini-dollar"}

# Function to fetch the top N coins by market cap excluding stablecoins
def fetch_top_coins(n=100):
    url = COINS_MARKET_ENDPOINT
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": n * 2,  # Fetch more coins to account for exclusions
        "page": 1,
        "sparkline": "false"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    # Exclude stablecoins
    coins = [coin['id'] for coin in data if coin['id'] not in EXCLUDED_STABLECOINS]
    return coins[:n]  # Return only the requested number of coins

# Function to fetch historical market cap data for a specific coin
def fetch_historical_market_cap(coin_id, days=365):
    url = COIN_MARKET_CHART_ENDPOINT.format(id=coin_id)
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    response = requests.get(url, params=params)
    if response.status_code == 429:
        # Rate limit exceeded, wait and retry
        print(f"Rate limit exceeded while fetching {coin_id}. Waiting for 60 seconds.")
        time.sleep(60)
        response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame({
        "Timestamp": pd.to_datetime([entry[0] for entry in data["market_caps"]], unit="ms"),
        f"{coin_id} Market Cap": [entry[1] for entry in data["market_caps"]]
    })

# Allow user to specify the number of coins to include
num_coins = 10

# Fetch the top coins by market cap excluding stablecoins
top_coins = fetch_top_coins(num_coins)

# Initialize an empty DataFrame for the final output
final_df = pd.DataFrame()

# Loop through the top coins to fetch Bitcoin and Ethereum data first
bitcoin_df = fetch_historical_market_cap("bitcoin")
ethereum_df = fetch_historical_market_cap("ethereum")

# Merge Bitcoin and Ethereum data on Timestamp
final_df = bitcoin_df.merge(ethereum_df, on="Timestamp", how="outer")

# Initialize an empty DataFrame for total market cap
total_market_cap_df = pd.DataFrame()

# Loop through each coin and fetch historical market cap data
for index, coin_id in enumerate(top_coins):
    print(f"Fetching data for {coin_id} ({index + 1}/{len(top_coins)})")
    coin_df = fetch_historical_market_cap(coin_id)
    if total_market_cap_df.empty:
        total_market_cap_df = coin_df
    else:
        total_market_cap_df = total_market_cap_df.merge(coin_df, on="Timestamp", how="outer")
    # Add a delay between requests
    time.sleep(10)

# Fill missing values with zero
total_market_cap_df = total_market_cap_df.fillna(0)

# Sum the market caps to approximate the total market cap
market_cap_columns = [col for col in total_market_cap_df.columns if col != "Timestamp"]
total_market_cap_df["Total Market Cap"] = total_market_cap_df[market_cap_columns].sum(axis=1)

# Merge total market cap data into the final DataFrame
final_df = final_df.merge(total_market_cap_df[["Timestamp", "Total Market Cap"]], on="Timestamp", how="outer")

# Calculate Bitcoin dominance and Altcoin dominance
final_df["Bitcoin Dominance (%)"] = (final_df["bitcoin Market Cap"] / final_df["Total Market Cap"]) * 100
final_df["Altcoin Dominance (%)"] = 100 - final_df["Bitcoin Dominance (%)"]

# Sort the DataFrame by Timestamp
final_df.sort_values("Timestamp", inplace=True)

# Reset the index after sorting
final_df.reset_index(drop=True, inplace=True)

# Select and rename columns for the final Excel file
final_df = final_df.rename(columns={
    "bitcoin Market Cap": "Bitcoin Market Cap",
    "ethereum Market Cap": "Ethereum Market Cap"
})
final_df = final_df[[
    "Timestamp", "Bitcoin Market Cap", "Ethereum Market Cap", "Total Market Cap",
    "Bitcoin Dominance (%)", "Altcoin Dominance (%)"
]]

# Save to Excel
final_df.to_excel(excel_file, index=False)
print(f"Historical total market cap data saved to {excel_file}")
