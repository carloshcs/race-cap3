import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set Streamlit to wide layout
st.set_page_config(layout="wide")

# File path for data
excel_file = "crypto_market_cap_history.xlsx"

# Function to load data from Excel
# Function to load data from Excel
# Function to load data from Excel, calculate missing columns, and filter out incomplete rows
def load_market_cap_data():
    try:
        # Read the Excel file and parse the Timestamp column
        market_cap_df = pd.read_excel(excel_file, parse_dates=["Timestamp"])

        # Ensure required columns are present
        required_columns = [
            "Timestamp",
            "Bitcoin Market Cap",
            "Ethereum Market Cap",
            "Total Market Cap",
            "Bitcoin Dominance (%)",
            "Altcoin Dominance (%)"
        ]
        missing_columns = [col for col in required_columns if col not in market_cap_df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        # Dynamically calculate 'Market Cap Excl Bitcoin' if missing
        if "Market Cap Excl Bitcoin" not in market_cap_df.columns:
            market_cap_df["Market Cap Excl Bitcoin"] = (
                market_cap_df["Total Market Cap"] - market_cap_df["Bitcoin Market Cap"]
            )

        # Drop rows with any missing data
        market_cap_df = market_cap_df.dropna()

        # Return the processed DataFrame
        return market_cap_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


# Load market cap data
market_cap_df = load_market_cap_data()

# Display a warning if no data is loaded
if market_cap_df.empty:
    st.warning("No data available. Please ensure the data file exists and contains valid data.")
    st.stop()

# Title of the dashboard
st.title("Cryptocurrency Market Cap and Dominance Dashboard")

# Date Range Filter with Button Style
st.markdown("### Select Date Range")
date_filter = st.radio(
    "",
    options=["7D", "1 Month", "3 Month", "All"],
    index=3,  # Default to "All"
    horizontal=True,
)

# Calculate the start date based on the selected filter
end_date = market_cap_df["Timestamp"].max()
if date_filter == "7D":
    start_date = end_date - pd.Timedelta(days=7)
elif date_filter == "1 Month":
    start_date = end_date - pd.Timedelta(days=30)
elif date_filter == "3 Month":
    start_date = end_date - pd.Timedelta(days=90)
else:  # "All"
    start_date = market_cap_df["Timestamp"].min()

# Filter data based on the selected date range
filtered_df = market_cap_df[
    (market_cap_df["Timestamp"] >= start_date) & (market_cap_df["Timestamp"] <= end_date)
]

# Sidebar filters
st.sidebar.header("Filters and Settings")

# Filter by coins
available_coins = ["Bitcoin Market Cap", "Ethereum Market Cap", "Total Market Cap", "Market Cap Excl Bitcoin"]
selected_coins = st.sidebar.multiselect(
    "Select Coins to Display",
    options=available_coins,
    default=available_coins,
    help="Choose which cryptocurrency market caps to visualize."
)

# If no coins are selected, warn the user
if not selected_coins:
    st.warning("No data to display. Please select at least one coin.")
    st.stop()

# Define the maximum width for the charts
MAX_CHART_WIDTH = 1000  # Specify your preferred maximum width here

# Central alignment container
def centered_chart(chart):
    """
    Centers the chart on the page by adding empty columns on the sides.
    """
    col1, col2, col3 = st.columns([1, 4, 1])  # Adjust proportions for centering
    with col2:
        st.plotly_chart(chart, use_container_width=False)

# Create the Plotly figure for Market Cap
market_cap_fig = go.Figure()

# Add traces for selected coins
for coin in selected_coins:
    market_cap_fig.add_trace(
        go.Scatter(
            x=filtered_df["Timestamp"],
            y=filtered_df[coin],
            mode="lines",
            name=coin
        )
    )

# Update layout for Market Cap chart
market_cap_fig.update_layout(
    title="<b>Cryptocurrency Market Cap Over Time</b>",
    xaxis=dict(title="<b>Date</b>", fixedrange=False, tickangle=45),
    yaxis=dict(title="<b>Market Cap (USD)</b>"),
    template="plotly_white",
    legend_title="Market Cap",
    margin=dict(l=20, r=20, t=40, b=40),  # Reasonable margins
    width=MAX_CHART_WIDTH,  # Set maximum width
    height=500,
)

# Create the Plotly figure for Dominance
dominance_fig = go.Figure()

# Add trace for Bitcoin Dominance
dominance_fig.add_trace(
    go.Scatter(
        x=filtered_df["Timestamp"],
        y=filtered_df["Bitcoin Dominance (%)"],
        mode="lines",
        name="Bitcoin Dominance (%)"
    )
)

# Add trace for Altcoin Dominance
dominance_fig.add_trace(
    go.Scatter(
        x=filtered_df["Timestamp"],
        y=filtered_df["Altcoin Dominance (%)"],
        mode="lines",
        name="Altcoin Dominance (%)"
    )
)

# Update layout for Dominance chart
dominance_fig.update_layout(
    title="<b>Bitcoin and Altcoin Dominance Over Time</b>",
    xaxis=dict(title="<b>Date</b>", fixedrange=False, tickangle=45),
    yaxis=dict(title="<b>Dominance (%)</b>"),
    template="plotly_white",
    legend_title="Dominance",
    margin=dict(l=20, r=20, t=40, b=40),  # Reasonable margins
    width=MAX_CHART_WIDTH,  # Set maximum width
    height=500,
)

# Display centered charts
centered_chart(market_cap_fig)
centered_chart(dominance_fig)
