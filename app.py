import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Analyzer", page_icon="📈", layout="wide")

# CSS Azul Moderno
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    .metric-card {
        background-color: #1c2333;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 STOCK EXCHANGE ANALYSIS")
st.caption("Análise Inteligente de Ações — Powered by Yahoo Finance")

ticker_input = st.text_input("Digite o código da ação (ex: AAPL, PETR4.SA)")

if ticker_input:
    ticker = yf.Ticker(ticker_input.upper())
    info = ticker.info

    if "currentPrice" in info:
        col1, col2, col3 = st.columns(3)

        col1.metric("💰 Preço Atual", f"${info.get('currentPrice')}")
        col2.metric("📊 Market Cap", f"{info.get('marketCap'):,}")
        col3.metric("📈 P/E Ratio", f"{info.get('trailingPE')}")

        st.subheader("📉 Histórico (3 meses)")
        hist = ticker.history(period="3mo")
        st.line_chart(hist["Close"])

        st.subheader("🏢 Sobre a Empresa")
        st.write(info.get("longBusinessSummary", "Sem descrição disponível."))

    else:
        st.error("Empresa não encontrada.")