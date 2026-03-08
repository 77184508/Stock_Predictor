from datetime import timedelta
import yfinance as yf
import pandas as pd
from database.db_connection import get_connection
from config.config import STOCK_SYMBOLS
from datetime import timedelta
def fetch_stock_data(symbol):

    last_date = get_last_date(symbol)

    if last_date is None:
        # first run
        data = yf.download(symbol, period="6mo", interval="1d")
    else:
        start_date = last_date + timedelta(days=1)

        data = yf.download(
            symbol,
            start=start_date,
            interval="1d"
        )

    data.reset_index(inplace=True)

    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    data["symbol"] = symbol

    return data
def store_data(df):
    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO stock_prices(symbol, date, open, high, low, close, volume)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (symbol, date) DO NOTHING
    """
    for _, row in df.iterrows():
        cursor.execute(
            insert_query,
            (
                str(row["symbol"]),
                row["Date"].date(),      
                float(row["Open"]),
                float(row["High"]),
                float(row["Low"]),
                float(row["Close"]),
                int(row["Volume"]),
            ),
        )

    conn.commit()
    cursor.close()
    conn.close()
def get_last_date(symbol):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT MAX(date)
        FROM stock_prices
        WHERE symbol = %s
        """,
        (symbol,)
    )

    result = cursor.fetchone()[0]
    print(result)
    cursor.close()
    conn.close()

    return result
def run_ingestion():

    for symbol in STOCK_SYMBOLS:
        df = fetch_stock_data(symbol)
        store_data(df)

if __name__ == "__main__":
    run_ingestion()