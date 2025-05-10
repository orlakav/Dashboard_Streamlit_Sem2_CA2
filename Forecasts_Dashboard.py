import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Stock Forecast Dashboard", layout="wide")
st.title("Stock Forecast Comparison")

# Sidebar
st.sidebar.header("Options")
tickers = ['AAPL', 'AMZN', 'TSLA', 'MSFT', 'BA']
models = ['lstm', 'arima', 'arimax', 'xgboost']
horizons = [1, 3, 7]

ticker = st.sidebar.selectbox("Select Company", tickers)
selected_models = st.sidebar.multiselect("Select Models", models, default=models)
selected_horizons = st.sidebar.multiselect("Select Horizons (days)", horizons, default=horizons)
show_sentiment = st.sidebar.checkbox("Show Sentiment Trend", value=True)

# main chart section... forecasts
st.subheader(f"{ticker} Forecast Timeline")

found_data = False
for model in selected_models:
    for horizon in selected_horizons:
        file_path = f"forecast_exports/{ticker}_{model}_{horizon}d_full.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, parse_dates=['date'])

            #ensure plot columns
            cols_to_plot = ['close']
            forecast_col = f"{model}_{horizon}d"
            if forecast_col in df.columns:
                cols_to_plot.append(forecast_col)

            #adding sentiment column if enabled
            sentiment_col = None
            if show_sentiment:
                if 'daily_sentiment' in df.columns:
                    sentiment_col = 'daily_sentiment'
                elif 'weekly_sentiment' in df.columns:
                    sentiment_col = 'weekly_sentiment'
                if sentiment_col and sentiment_col not in cols_to_plot:
                    cols_to_plot.append(sentiment_col)

            #plot
            fig = px.line(
                df,
                x='date',
                y=cols_to_plot,
                labels={'value': 'Price / Sentiment', 'variable': 'Series'},
                title=f"{ticker} - {model.upper()} Forecast ({horizon}-Day)",
                template="plotly_white"
            )
            fig.update_traces(mode='lines+markers')
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            found_data = True

if not found_data:
    st.warning("No forecast data found for selected options.")

# RMSE Table
st.subheader("RMSE Scores")
rmse_path = "forecast_exports/rmse_summary.csv"
if os.path.exists(rmse_path):
    df_rmse = pd.read_csv(rmse_path)
    filtered_rmse = df_rmse[df_rmse['ticker'] == ticker]
    st.dataframe(filtered_rmse)
else:
    st.info("No RMSE summary file found.")

# Footer
st.markdown("---")
st.caption("Orla Kavanagh CA2 CCT MSc Data Analytics")
