import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Stock Forecast Dashboard", layout="wide")

st.title("Stock Forecast Dashboard")

#sidebar
st.sidebar.header("Forecast Settings")
tickers = ['AAPL', 'AMZN', 'TSLA', 'MSFT', 'BA']
models = ['lstm', 'arima', 'arimax', 'sarimax', 'xgboost']
horizons = [1, 3, 7]

ticker = st.sidebar.selectbox("Select Company", tickers)
model = st.sidebar.selectbox("Select Forecasting Model", models)
horizon = st.sidebar.selectbox("Select Forecast Horizon (days)", horizons)
show_sentiment = st.sidebar.checkbox("Overlay Sentiment Trend (if available)", value=True)

#loading Forecast Data
forecast_path = f"forecast_exports/{ticker}_{model}_{horizon}d.csv"

if os.path.exists(forecast_path):
    df = pd.read_csv(forecast_path, parse_dates=['date'])

    # Forecast Plot
    fig = px.line(df, x='date', y=['actual', 'forecast'],
                  labels={'value': 'Close Price', 'variable': 'Type'},
                  title=f"{ticker} {model.upper()} Forecast ({horizon}-Day)")
    fig.update_traces(mode='lines+markers')
    fig.update_layout(hovermode='x unified', template='plotly_white')

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning(f"No forecast file found for {ticker} {model} {horizon}-day.")

# RMSE table
rmse_path = "forecast_exports/rmse_summary.csv"
if os.path.exists(rmse_path):
    df_rmse = pd.read_csv(rmse_path)
    filtered = df_rmse[(df_rmse['ticker'] == ticker)]
    st.subheader("RMSE Scores")
    st.dataframe(filtered)
else:
    st.warning("RMSE summary file is missing.")

# sentiment overlay
if show_sentiment:
    sent_path = f"forecast_exports/{ticker}_sentiment_trend.csv"
    if os.path.exists(sent_path):
        df_sent = pd.read_csv(sent_path, parse_dates=['date'])
        fig_sent = px.line(df_sent, x='date', y=df_sent.columns[1],
                           title=f"{ticker} Sentiment Trend",
                           labels={'value': 'Sentiment Score'},
                           template='plotly_white')
        fig_sent.update_traces(mode='lines+markers')
        st.plotly_chart(fig_sent, use_container_width=True)
    else:
        st.info(f"No sentiment trend file found for {ticker}.")

# Footer
st.markdown("---")
st.caption("Built using Streamlit and Plotly – MSc Project")
