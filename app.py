# Import libraries
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import sum, col, when, max, lag
from snowflake.snowpark import Window
from datetime import timedelta
import altair as alt
import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(layout="wide")

# Get current session
session = get_active_session()

@st.cache_data()
def load_data():
    # Load and transform daily stock price data.
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

    # Load foreign exchange (FX) rates data.
    snow_df_fx = session.table("FINANCE__ECONOMICS.CYBERSYN.FX_RATES_TIMESERIES").filter(
        (col('BASE_CURRENCY_ID') == 'EUR') & (col('DATE') >= '2019-01-01')).with_column_renamed('VARIABLE_NAME','EXCHANGE_RATE')
    
    return snow_df_stocks_transformed.to_pandas(), snow_df_fx.to_pandas()

# Load and cache data
df_stocks, df_fx = load_data()

def stock_prices():
    st.subheader('Stock Performance on the Nasdaq for the Magnificent 7')
    
    df_stocks['DATE'] = pd.to_datetime(df_stocks['DATE'])
    max_date = df_stocks['DATE'].max()  # Most recent date
    min_date = df_stocks['DATE'].min()  # Earliest date
    
    # Default start date as 30 days before the most recent date
    default_start_date = max_date - timedelta(days=30)

    # Use the adjusted default start date in the 'date_input' widget
    start_date, end_date = st.date_input("Date range:", [default_start_date, max_date], min_value=min_date, max_value=max_date, key='date_range')
    start_date_ts = pd.to_datetime(start_date)
    end_date_ts = pd.to_datetime(end_date)

    # Filter DataFrame based on the selected date range
    df_filtered = df_stocks[(df_stocks['DATE'] >= start_date_ts) & (df_stocks['DATE'] <= end_date_ts)]
    
    # Ticker filter with multi-selection and default values
    unique_tickers = df_filtered['TICKER'].unique().tolist()
    default_tickers = [ticker for ticker in ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA'] if ticker in unique_tickers]
    selected_tickers = st.multiselect('Ticker(s):', unique_tickers, default=default_tickers)
    df_filtered = df_filtered[df_filtered['TICKER'].isin(selected_tickers)]
    
    # Metric selection
    metric = st.selectbox('Metric:',('DAY_OVER_DAY_CHANGE','POSTMARKET_CLOSE','NASDAQ_VOLUME'), index=0) # Default to DAY_OVER_DAY_CHANGE
    
    # Generate and display line chart for selected ticker(s) and metric
    line_chart = alt.Chart(df_filtered).mark_line().encode(
        x='DATE',
        y=alt.Y(metric, title=metric),
        color='TICKER',
        tooltip=['TICKER','DATE',metric]
    ).interactive()
    st.altair_chart(line_chart, use_container_width=True)

def fx_rates():
    st.subheader('EUR Exchange (FX) Rates by Currency Over Time')

    # GBP, CAD, USD, JPY, PLN, TRY, CHF
    currencies = ['British Pound Sterling','Canadian Dollar','United States Dollar','Japanese Yen','Polish Zloty','Turkish Lira','Swiss Franc']
    selected_currencies = st.multiselect('', currencies, default = ['British Pound Sterling','Canadian Dollar','United States Dollar','Swiss Franc','Polish Zloty'])
    st.markdown("___")

    # Display an interactive chart to visualize exchange rates over time by the selected currencies
    with st.container():
        currencies_list = currencies if len(selected_currencies) == 0 else selected_currencies
        df_fx_filtered = df_fx[df_fx['QUOTE_CURRENCY_NAME'].isin(currencies_list)]
        line_chart = alt.Chart(df_fx_filtered).mark_line(
            color="lightblue",
            line=True,
        ).encode(
            x='DATE',
            y='VALUE',
            color='QUOTE_CURRENCY_NAME',
            tooltip=['QUOTE_CURRENCY_NAME','DATE','VALUE']
        )
        st.altair_chart(line_chart, use_container_width=True)

# Display header
st.header("Cybersyn: Financial & Economic Essentials")

# Create sidebar and load the first page
page_names_to_funcs = {
    "Daily Stock Performance Data": stock_prices,
    "Exchange (FX) Rates": fx_rates
}
selected_page = st.sidebar.selectbox("Select", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
