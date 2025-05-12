import streamlit as st
import pandas as pd
import plotly.express as px
import os
import glob

st.set_page_config(page_title="Stock Forecast Dashboard", layout="wide")
st.title("Stock Forecast Dashboard")

# ticker dropdown
tickers = ['AAPL', 'AMZN', 'TSLA', 'MSFT', 'BA']
ticker = st.selectbox("Choose a company to explore:", tickers)

# Forecast merging setup
models = ['lstm', 'arima', 'arimax', 'xgboost']
horizons = [1, 3, 7]
dfs = []
forecast_cols = []
max_forecast_date = None

# loading all relevant forecast files
for model in models:
    for horizon in horizons:
        file_paths = glob.glob(f"forecast_exports/{ticker}_{model}_{horizon}d_full*.csv")
        for file_path in file_paths:
            df = pd.read_csv(file_path, parse_dates=['date'])

            forecast_col = f"{model}_{horizon}d"
            if "tuned" in file_path:
                forecast_col += "_tuned"
            original_col = f"{model}_{horizon}d"
            if original_col in df.columns and not df.empty:
                df.rename(columns={original_col: forecast_col}, inplace=True)
            if not dfs:
                df = df[['date', 'close'] + [forecast_col] +
                        [col for col in ['daily_sentiment', 'weekly_sentiment'] if col in df.columns]]
            else:
                df = df[['date'] + [forecast_col]]
            df = df.drop_duplicates(subset='date')
            df.set_index('date', inplace=True)

            # Track the latest forecast date
            last_forecast = df[forecast_col].dropna()
            if not last_forecast.empty:
                last_date = last_forecast.index.max()
                if max_forecast_date is None or last_date > max_forecast_date:
                    max_forecast_date = last_date

            forecast_cols.append(forecast_col)
            dfs.append(df)

# merge forecasts and truncate stock data
if dfs:
    base_df = dfs[0][['close']].copy()
    base_df.index = dfs[0].index  # set same index

    for df in dfs:
        for col in df.columns:
            if col not in base_df.columns and col != 'close':
                base_df[col] = df[col]
#converting index back to column for Plotly
    merged_df = base_df.reset_index()

    if max_forecast_date:
        merged_df = merged_df[merged_df['date'] <= max_forecast_date]

    # plot forecast chart
    st.subheader(f"Forecast Comparison for {ticker}")

    # renaming 'close' column so looks better in legend
    merged_df = merged_df.rename(columns={'close': 'Actual Close Price'})
    cols_to_plot = ['Actual Close Price'] + forecast_cols
    hover_cols = []
    if 'daily_sentiment' in merged_df.columns:
        hover_cols.append('daily_sentiment')
    elif 'weekly_sentiment' in merged_df.columns:
        hover_cols.append('weekly_sentiment')

    fig = px.line(
        merged_df,
        x='date',
        y=cols_to_plot,
        title=f"{ticker} - Stock Price & Forecasts (Use legend to toggle models)",
        labels={'value': 'Price', 'variable': 'Series'},
        hover_data=hover_cols if hover_cols else None,
        template='plotly_white'
    )
    fig.update_traces(mode='lines+markers')
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No forecast data found for this ticker.")

# Sentiment plot
st.subheader(f"Sentiment Trend for {ticker}")
show_sentiment_plot = st.checkbox("Show sentiment plot", value=False)

if show_sentiment_plot:
    sentiment_df = None
    for df in dfs:
        if 'daily_sentiment' in df.columns:
            sentiment_df = df[['daily_sentiment']].dropna().reset_index()
            sentiment_df = sentiment_df.rename(columns={'daily_sentiment': 'sentiment'})
            break
        elif 'weekly_sentiment' in df.columns:
            sentiment_df = df[['weekly_sentiment']].dropna().reset_index()
            sentiment_df = sentiment_df.rename(columns={'weekly_sentiment': 'sentiment'})
            break

    if sentiment_df is not None and not sentiment_df.empty:
        fig_sent = px.line(
            sentiment_df,
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
        st.info("No sentiment data available.")

# RMSE Table
st.subheader("RMSE Scores")

rmse_path = "forecast_exports/rmse_summary.csv"
if os.path.exists(rmse_path):
    df_rmse = pd.read_csv(rmse_path)

    # filter widgets
    st.markdown("**Filter RMSE Table:**")
    rmse_tickers = st.multiselect("Ticker(s)", tickers, default=tickers)
    model_options = ['lstm', 'lstm_tuned', 'arima', 'arimax', 'xgboost']
    rmse_models = st.multiselect("Model(s)", model_options, default=model_options)
    rmse_horizons = st.multiselect("Horizon(s)", horizons, default=horizons)

    filtered = df_rmse[
        df_rmse['ticker'].isin(rmse_tickers) &
        df_rmse['model'].isin(rmse_models) &
        df_rmse['horizon'].isin(rmse_horizons)
    ]

    st.dataframe(filtered)
else:
    st.info("RMSE summary file not found.")

# footer
st.markdown("---")
st.caption("Orla Kavanagh CA2 | CCT MSc Data Analytics")