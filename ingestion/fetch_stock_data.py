import yfinance as yf
import pandas as pd
from database.db_connection import get_connection
from config.config import STOCK_SYMBOLS

def fetch_stock_data(symbol):
    data = yf.download(symbol, period="1mo", interval="1d")

    data.reset_index(inplace=True)
    data["symbol"] = symbol

    return data

def store_data(df):
    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO stock_prices(symbol, date, open, high, low, close, volume)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (symbol, date) DO NOTHING
            """,
            (
                row["symbol"],
                row["Date"],
                row["Open"],
                row["High"],
                row["Low"],
                row["Close"],
                row["Volume"],
            ),
        )

    conn.commit()
    cursor.close()
    conn.close()

def run_ingestion():

    for symbol in STOCK_SYMBOLS:
        df = fetch_stock_data(symbol)
        store_data(df)

if __name__ == "__main__":
    run_ingestion()