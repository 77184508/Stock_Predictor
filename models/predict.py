import joblib
import pandas as pd
from database.db_connection import get_connection
from datetime import timedelta


def load_latest_features():
    """
    Load the newest feature rows (latest date)
    """

    conn = get_connection()

    query = """
    SELECT *
    FROM stock_features
    WHERE date = (SELECT MAX(date) FROM stock_features)
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df


def predict(df):
    """
    Generate predictions using the trained model
    """

    model = joblib.load("models/model.pkl")

    X = df.drop(columns=[
        "symbol",
        "date",
        "target_return"
    ])

    df["predicted_return"] = model.predict(X)

    df["predicted_price"] = df["close"] * (1 + df["predicted_return"])

    df["date"] = df["date"] + timedelta(days=1)
    return df


def store_predictions(df):
    """
    Insert predictions into predictions table
    """

    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO predictions(
        symbol,
        date,
        predicted_return,
        predicted_price,
        model_name
    )
    VALUES (%s,%s,%s,%s,%s)
    ON CONFLICT (symbol, date, model_name) DO NOTHING
    """

    for _, row in df.iterrows():

        cursor.execute(
            insert_query,
            (
                row["symbol"],
                row["date"],
                row["predicted_return"],
                row["predicted_price"],
                "xgboost"
            )
        )

    conn.commit()
    cursor.close()
    conn.close()


def main():

    print("Loading latest features...")

    df = load_latest_features()

    print("Generating predictions...")

    df = predict(df)

    print("Storing predictions...")

    store_predictions(df)

    print("Prediction pipeline completed.")


if __name__ == "__main__":
    main()