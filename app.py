# Import required libraries
from snowflake.snowpark import Session
from snowflake.snowpark.functions import sum, col, when, max, lag
from snowflake.snowpark import Window
from datetime import timedelta
import altair as alt
import streamlit as st
import pandas as pd

# Set Streamlit page configuration
st.set_page_config(layout="wide")

# Load Snowflake connection settings from Streamlit secrets
connection_parameters = {
    "account": st.secrets["snowflake"]["account"],
    "user": st.secrets["snowflake"]["user"],
    "password": st.secrets["snowflake"]["password"],
    "role": st.secrets["snowflake"]["role"],
    "warehouse": st.secrets["snowflake"]["warehouse"],
    "database": st.secrets["snowflake"]["database"],
    "schema": st.secrets["snowflake"]["schema"],
}

# Create Snowflake session
try:
    session = Session.builder.configs(connection_parameters).create()
    st.success("Snowflake session successfully created!")
except Exception as e:
    st.error(f"Error creating Snowflake session: {e}")
    session = None  # Ensure session is set to None if initialization fails

@st.cache_data()
def load_data(session):
    if not session:
        st.error("No active Snowflake session. Please check your connection.")
        return None, None

    # Load and transform daily stock price data
    snow_df_stocks = (
        session.table("FINANCE__ECONOMICS.CYBERSYN.STOCK_PRICE_TIMESERIES")
        .filter(
            (col('TICKER').isin('AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA')) & 
            (col('VARIABLE_NAME').isin('Nasdaq Volume', 'Post-Market Close')))
        .groupBy("TICKER", "DATE")
        .agg(
            max(when(col("VARIABLE_NAME") == "Nasdaq Volume", col("VALUE"))).alias("NASDAQ_VOLUME"),
            max(when(col("VARIABLE_NAME") == "Post-Market Close", col("VALUE"))).alias("POSTMARKET_CLOSE")
        )
    )
    
    # Adding the Day over Day Post-market Close Change calculation
    window_spec = Window.partitionBy("TICKER").orderBy("DATE")
    snow_df_stocks_transformed = snow_df_stocks.withColumn("DAY_OVER_DAY_CHANGE", 
        (col("POSTMARKET_CLOSE") - lag(col("POSTMARKET_CLOSE"), 1).over(window_spec)) /
        lag(col("POSTMARKET_CLOSE"), 1).over(window_spec)
    )

    # Load foreign exchange (FX) rates data
    snow_df_fx = session.table("FINANCE__ECONOMICS.CYBERSYN.FX_RATES_TIMESERIES").filter(
        (col('BASE_CURRENCY_ID') == 'EUR') & (col('DATE') >= '2019-01-01')).with_column_renamed('VARIABLE_NAME','EXCHANGE_RATE')
    
    return snow_df_stocks_transformed.to_pandas(), snow_df_fx.to_pandas()

# Ensure session is active before loading data
if session:
    df_stocks, df_fx = load_data(session)
else:
    df_stocks, df_fx = None, None

def stock_prices():
    if df_stocks is None:
        st.error("Data could not be loaded. Please check your Snowflake connection.")
        return
    
    st.subheader('Stock Performance on the Nasdaq for the Magnificent 7')
    df_stocks['DATE'] = pd.to_datetime(df_stocks['DATE'])
    max_date = df_stocks['DATE'].max()
    min_date = df_stocks['DATE'].min()
    default_start_date = max_date - timedelta(days=30)
    start_date, end_date = st.date_input("Date range:", [default_start_date, max_date], min_value=min_date, max_value=max_date)
    df_filtered = df_stocks[(df_stocks['DATE'] >= pd.to_datetime(start_date)) & (df_stocks['DATE'] <= pd.to_datetime(end_date))]
    selected_tickers = st.multiselect('Ticker(s):', df_filtered['TICKER'].unique(), default=['AAPL', 'MSFT'])
    df_filtered = df_filtered[df_filtered['TICKER'].isin(selected_tickers)]
    metric = st.selectbox('Metric:', ('DAY_OVER_DAY_CHANGE', 'POSTMARKET_CLOSE', 'NASDAQ_VOLUME'), index=0)
    line_chart = alt.Chart(df_filtered).mark_line().encode(
        x='DATE',
        y=metric,
        color='TICKER',
        tooltip=['TICKER', 'DATE', metric]
    ).interactive()
    st.altair_chart(line_chart, use_container_width=True)

def fx_rates():
    if df_fx is None:
        st.error("Data could not be loaded. Please check your Snowflake connection.")
        return
    
    st.subheader('EUR Exchange (FX) Rates by Currency Over Time')
    currencies = ['British Pound Sterling', 'Canadian Dollar', 'United States Dollar', 'Japanese Yen']
    selected_currencies = st.multiselect('', currencies, default=currencies[:3])
    df_fx_filtered = df_fx[df_fx['QUOTE_CURRENCY_NAME'].isin(selected_currencies)]
    line_chart = alt.Chart(df_fx_filtered).mark_line().encode(
        x='DATE',
        y='VALUE',
        color='QUOTE_CURRENCY_NAME',
        tooltip=['QUOTE_CURRENCY_NAME', 'DATE', 'VALUE']
    )
    st.altair_chart(line_chart, use_container_width=True)

# Display header and sidebar
st.header("Cybersyn: Financial & Economic Essentials")
page_names_to_funcs = {"Daily Stock Performance Data": stock_prices, "Exchange (FX) Rates": fx_rates}
selected_page = st.sidebar.selectbox("Select", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
