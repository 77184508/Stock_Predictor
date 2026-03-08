import pandas as pd
from database.db_connection import get_connection
from config.config import STOCK_SYMBOLS


def load_price_data(symbol):
    """
    Load historical stock prices from database
    """

    conn = get_connection()

    query = """
    SELECT date, close
    FROM stock_prices
    WHERE symbol = %s
    ORDER BY date
    """

    df = pd.read_sql(query, conn, params=(symbol,))
    conn.close()

    return df


def compute_features(df):
    """
    Compute time-series features
    """

    # ensure sorted
    df = df.sort_values("date")

    # daily returns
    df["return_1d"] = df["close"].pct_change()

    # moving averages
    df["ma_7"] = df["close"].rolling(7).mean()
    df["ma_21"] = df["close"].rolling(21).mean()

    # volatility
    df["volatility"] = df["return_1d"].rolling(21).std()

    # momentum
    df["momentum"] = df["close"] - df["close"].shift(10)
    # lag features
    df["lag_1"] = df["close"].shift(1)
    df["lag_5"] = df["close"].shift(5)
    df["lag_10"] = df["close"].shift(10)
    df["target_return"] = df["return_1d"].shift(-1)

    return df


def store_features(symbol, df):
    """
    Insert computed features into database
    """

    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO stock_features(
    symbol, date, close,
    return_1d, ma_7, ma_21,
    volatility, lag_1, lag_5, lag_10,
    momentum, target_return
)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON CONFLICT (symbol, date) DO NOTHING
"""

    for _, row in df.iterrows():

        cursor.execute(
            insert_query,
            (
symbol,
row["date"],
row["close"],
row["return_1d"],
row["ma_7"],
row["ma_21"],
row["volatility"],
row["lag_1"],
row["lag_5"],
row["lag_10"],
row["momentum"],
row["target_return"]
),
        )

    conn.commit()
    cursor.close()
    conn.close()


def run_feature_pipeline(symbol):

    df = load_price_data(symbol)

    df = compute_features(df)

    store_features(symbol, df)


if __name__ == "__main__":

    for symbol in STOCK_SYMBOLS:

        print(f"Generating features for {symbol}")

        run_feature_pipeline(symbol)