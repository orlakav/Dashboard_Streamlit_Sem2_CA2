import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Stock Forecast Dashboard", layout="wide")
st.title("Stock Forecast Dashboard")

# choosing ticker
tickers = ['AAPL', 'AMZN', 'TSLA', 'MSFT', 'BA']
ticker = st.selectbox("Choose a company to explore:", tickers)

# show RMSE Table
st.subheader(f"RMSE Scores for {ticker}")
rmse_path = "forecast_exports/rmse_summary.csv"
if os.path.exists(rmse_path):
    df_rmse = pd.read_csv(rmse_path)
    filtered_rmse = df_rmse[df_rmse['ticker'] == ticker]
    st.dataframe(filtered_rmse)
else:
    st.warning("RMSE summary file not found.")

# Forecast plot options
models = ['lstm', 'arima', 'arimax', 'xgboost']
horizons = [1, 3, 7]
show_sentiment = st.checkbox("Overlay sentiment trend (if available)", value=True)

# forecast plots
for model in models:
    for horizon in horizons:
        file_path = f"forecast_exports/{ticker}_{model}_{horizon}d_full.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, parse_dates=['date'])
            except Exception as e:
                st.error(f"Error reading {file_path}: {e}")
                continue

            cols_to_plot = ['close']
            forecast_col = f"{model}_{horizon}d"
            if forecast_col in df.columns:
                cols_to_plot.append(forecast_col)

            # Add in sentiment if clicked
            if show_sentiment:
                if 'daily_sentiment' in df.columns:
                    cols_to_plot.append('daily_sentiment')
                elif 'weekly_sentiment' in df.columns:
                    cols_to_plot.append('weekly_sentiment')

            fig = px.line(
                df,
                x='date',
                y=cols_to_plot,
                title=f"{ticker} - {model.upper()} Forecast ({horizon}-Day)",
                labels={'value': 'Price / Sentiment', 'variable': 'Series'},
                template='plotly_white'
            )
            fig.update_traces(mode='lines+markers')
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

# footer
st.markdown("---")
st.caption("Orla Kavanagh CA2 | CCT MSc Data Analytics")
