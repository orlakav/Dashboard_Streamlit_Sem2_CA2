import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Stock Forecast Dashboard", layout="wide")
st.title("Stock Forecast Dashboard")

# Ticker options-
tickers = ['AAPL', 'AMZN', 'TSLA', 'MSFT', 'BA']
ticker = st.selectbox("Choose a company to explore:", tickers)

# Plot options for forecasts
models = ['lstm', 'arima', 'arimax', 'xgboost']
horizons = [1, 3, 7]

# Forecast plot
st.subheader(f"Forecasts for {ticker}")
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

            # Tooltips with sentiment
            hover_data = {}
            if 'daily_sentiment' in df.columns:
                hover_data['daily_sentiment'] = True
            elif 'weekly_sentiment' in df.columns:
                hover_data['weekly_sentiment'] = True

            fig = px.line(
                df,
                x='date',
                y=cols_to_plot,
                title=f"{ticker} - {model.upper()} Forecast ({horizon}-Day)",
                labels={'value': 'Price', 'variable': 'Series'},
                template='plotly_white',
                hover_data=hover_data if hover_data else None
            )
            fig.update_traces(mode='lines+markers')
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

# Sentiment plot
st.subheader(f"Sentiment Trend for {ticker}")
show_sentiment_plot = st.checkbox("Show sentiment trend chart", value=False)

if show_sentiment_plot:
    sentiment_cols = ['daily_sentiment', 'weekly_sentiment']
    sentiment_file = None
    for model in models:
        for horizon in horizons:
            path = f"forecast_exports/{ticker}_{model}_{horizon}d_full.csv"
            if os.path.exists(path):
                df = pd.read_csv(path, parse_dates=['date'])
                for col in sentiment_cols:
                    if col in df.columns:
                        sentiment_file = df[['date', col]]
                        sentiment_file = sentiment_file.dropna().drop_duplicates()
                        sentiment_file = sentiment_file.rename(columns={col: 'sentiment'})
                        break
                if sentiment_file is not None:
                    break

    if sentiment_file is not None and not sentiment_file.empty:
        fig_sent = px.line(
            sentiment_file,
            x='date',
            y='sentiment',
            title=f"{ticker} Sentiment Trend",
            labels={'sentiment': 'Sentiment Score'},
            template='plotly_white'
        )
        fig_sent.update_traces(mode='lines+markers')
        fig_sent.update_layout(hovermode='x unified')
        st.plotly_chart(fig_sent, use_container_width=True)
    else:
        st.info("No sentiment data available for this ticker.")

# RMSE Table
st.subheader(f"RMSE Scores for {ticker}")
rmse_path = "forecast_exports/rmse_summary.csv"
if os.path.exists(rmse_path):
    df_rmse = pd.read_csv(rmse_path)
    filtered_rmse = df_rmse[df_rmse['ticker'] == ticker]
    st.dataframe(filtered_rmse)
else:
    st.warning("RMSE summary file not found.")

#footer
st.markdown("---")
st.caption("Orla Kavanagh CA2 | CCT MSc Data Analytics")
