import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Stock Forecast Dashboard", layout="wide")
st.title("Stock Forecast Dashboard")

# Ticker dropdown for main chart
tickers = ['AAPL', 'AMZN', 'TSLA', 'MSFT', 'BA']
ticker = st.selectbox("Choose a company to explore:", tickers)

# Forecast plot per company with toggled models
models = ['lstm', 'arima', 'arimax', 'xgboost']
horizons = [1, 3, 7]

# load all relevant forecast files for the company
dfs = []
forecast_cols = []
max_forecast_date = None

for model in models:
    for horizon in horizons:
        file_path = f"forecast_exports/{ticker}_{model}_{horizon}d_full.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, parse_dates=['date'])

            forecast_col = f"{model}_{horizon}d"
            if forecast_col in df.columns:
                if df.empty:
                    continue
                df = df[['date', 'close'] + [forecast_col] +
                        [col for col in ['daily_sentiment', 'weekly_sentiment'] if col in df.columns]]
                dfs.append(df)
                forecast_cols.append(forecast_col)

                # Track latest forecast date
                last_forecast_date = df[df[forecast_col].notna()]['date'].max()
                if last_forecast_date:
                    if max_forecast_date is None or last_forecast_date > max_forecast_date:
                        max_forecast_date = last_forecast_date

# Merge & truncate to latest forecast date so no more "floating" forecasts
if dfs:
    merged_df = pd.concat(dfs).drop_duplicates('date').sort_values('date')
    merged_df = merged_df.set_index('date')
    merged_df = merged_df[~merged_df.index.duplicated(keep='first')]
    merged_df = merged_df.reset_index()

    if max_forecast_date:
        merged_df = merged_df[merged_df['date'] <= max_forecast_date]

    # plotting forecast comparison
    st.subheader(f"Forecast Comparison for {ticker}")
    cols_to_plot = ['close'] + forecast_cols
    hover_cols = []
    if 'daily_sentiment' in merged_df.columns:
        hover_cols.append('daily_sentiment')
    elif 'weekly_sentiment' in merged_df.columns:
        hover_cols.append('weekly_sentiment')

    fig = px.line(
        merged_df,
        x='date',
        y=cols_to_plot,
        title=f"{ticker} Stock & Forecasts (Toggle in legend)",
        labels={'value': 'Price', 'variable': 'Series'},
        hover_data=hover_cols if hover_cols else None,
        template='plotly_white'
    )
    fig.update_traces(mode='lines+markers')
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No forecast data found for this ticker.")

# optional Sentiment Plot
st.subheader(f"Sentiment Trend for {ticker}")
show_sentiment_plot = st.checkbox("Show sentiment chart", value=False)

if show_sentiment_plot:
    sentiment_path = None
    for model in models:
        for horizon in horizons:
            path = f"forecast_exports/{ticker}_{model}_{horizon}d_full.csv"
            if os.path.exists(path):
                df_sent = pd.read_csv(path, parse_dates=['date'])
                for col in ['daily_sentiment', 'weekly_sentiment']:
                    if col in df_sent.columns:
                        sentiment_path = df_sent[['date', col]].dropna().drop_duplicates()
                        sentiment_path = sentiment_path.rename(columns={col: 'sentiment'})
                        break
                if sentiment_path is not None:
                    break

    if sentiment_path is not None:
        fig_sent = px.line(
            sentiment_path,
            x='date',
            y='sentiment',
            title=f"{ticker} Sentiment Over Time",
            labels={'sentiment': 'Sentiment Score'},
            template='plotly_white'
        )
        fig_sent.update_traces(mode='lines+markers')
        fig_sent.update_layout(hovermode='x unified')
        st.plotly_chart(fig_sent, use_container_width=True)
    else:
        st.info("No sentiment data found.")

# RMSE Table with option to choose multiple tickers/models/horizons 
st.subheader("RMSE Comparison Table")

rmse_path = "forecast_exports/rmse_summary.csv"
if os.path.exists(rmse_path):
    df_rmse = pd.read_csv(rmse_path)

    # filters
    rmse_tickers = st.multiselect("Filter by Ticker", tickers, default=tickers)
    rmse_models = st.multiselect("Filter by Model", models, default=models)
    rmse_horizons = st.multiselect("Filter by Horizon (days)", horizons, default=horizons)

    #apply filters
    filtered = df_rmse[
        df_rmse['ticker'].isin(rmse_tickers) &
        df_rmse['model'].isin(rmse_models) &
        df_rmse['horizon'].isin(rmse_horizons)
    ]
    st.dataframe(filtered)
else:
    st.warning("RMSE summary file not found.")

# footer
st.markdown("---")
st.caption("Orla Kavanagh's CA2 | CCT MSc Data Analytics")

