# Cybersyn: Financial & Economic Essentials


## Overview
This Streamlit app provides an interactive platform to analyze and visualize financial and economic data. With two main features—daily stock performance of major companies and exchange (FX) rates for key currencies—this app empowers users to gain insights and make data-driven decisions.

### Features
1. **Daily Stock Performance Data**:
   - Analyze the performance of the "Magnificent 7" stocks (AAPL, MSFT, AMZN, GOOGL, META, TSLA, NVDA) on the Nasdaq.
   - Visualize metrics such as day-over-day changes, post-market close values, and Nasdaq trading volume.
   - Interactive filtering by date range, stock tickers, and metrics.

2. **Exchange (FX) Rates**:
   - View and analyze historical FX rates for key currencies such as GBP, CAD, USD, JPY, PLN, TRY, and CHF.
   - Filter by currencies of interest.
   - Interactive line charts for trends over time.

---

## Technology Stack
- **Python Libraries**: 
  - `streamlit`: For building the interactive user interface.
  - `altair`: For creating interactive visualizations.
  - `snowflake.snowpark`: For fetching and transforming data from Snowflake.
  - `pandas`: For data manipulation and analysis.
- **Snowflake**:
  - Data source for financial stock data and FX rates.

---

## Installation and Setup
### Prerequisites
1. A working Snowflake account with the necessary databases and tables:
   - `FINANCE__ECONOMICS.CYBERSYN.STOCK_PRICE_TIMESERIES`
   - `FINANCE__ECONOMICS.CYBERSYN.FX_RATES_TIMESERIES`
2. Python 3.9 or later installed.

### Installation Steps
1. Clone this repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```
2. Install required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure `streamlit secrets` for Snowflake credentials:
   ```toml
   [snowflake]
   account = "your_account.snowflakecomputing.com"
   user = "your_username"
   password = "your_password"
   role = "your_role"
   warehouse = "your_warehouse"
   database = "FINANCE__ECONOMICS"
   schema = "CYBERSYN"
   ```
   Save this configuration in `.streamlit/secrets.toml`.

4. Run the app:
   ```bash
   streamlit run app.py
   ```

---

## Usage Instructions
### Daily Stock Performance Data
1. Navigate to the "Daily Stock Performance Data" page from the sidebar.
2. Select a date range to filter the stock data.
3. Choose the tickers and metrics you want to visualize.
4. View interactive line charts for selected data.

### Exchange (FX) Rates
1. Navigate to the "Exchange (FX) Rates" page from the sidebar.
2. Select currencies of interest.
3. View the FX trends on an interactive line chart.

---

## Data Sources
1. **Stock Data**: Pulled from Snowflake's `STOCK_PRICE_TIMESERIES` table.
2. **FX Rates Data**: Pulled from Snowflake's `FX_RATES_TIMESERIES` table.

---

## Future Enhancements
- Add more metrics and visualizations for deeper financial analysis.
- Incorporate predictive models for stock and FX rates.
- Enable user-specific data uploads for custom analysis.

---

## Screenshots
1. **Stock Performance Dashboard**
   - Visualize daily performance metrics for major Nasdaq stocks.
2. **FX Rates Analysis**
   - Track historical trends for key currency exchange rates.

---

## License
This project is open-source and available under the MIT License.

---

## Feedback and Contributions
Please submit a pull request if you'd like to enhance this app. 
