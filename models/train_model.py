import pandas as pd
import joblib

from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

from database.db_connection import get_connection


def load_features():
    """
    Load engineered features from database
    """

    conn = get_connection()

    query = """
    SELECT *
    FROM stock_features
    ORDER BY date
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


def prepare_dataset(df):
    """
    Prepare feature matrix X and target y
    """

    df = df.dropna()

    X = df.drop(columns=[
        "symbol",
        "date",
        "target_return"
    ])

    y = df["target_return"]

    return X, y


def train_test_split_time_series(X, y, split_ratio=0.8):
    """
    Time-series split
    """

    split_index = int(len(X) * split_ratio)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    return X_train, X_test, y_train, y_test


def train_model(X_train, y_train):
    """
    Train XGBoost model
    """

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    return model


def evaluate_model(model, X_test, y_test):

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)

    print("\nModel Performance")
    print("-----------------")
    print("MAE:", mae)
    print("MSE:", mse)

    return predictions


def show_feature_importance(model, X_train):

    importance = pd.Series(
        model.feature_importances_,
        index=X_train.columns
    ).sort_values(ascending=False)

    print("\nFeature Importance")
    print("------------------")
    print(importance)


def save_model(model):

    joblib.dump(model, "models/model.pkl")

    print("\nModel saved to models/model.pkl")


def main():

    print("Loading features...")

    df = load_features()

    print("Preparing dataset...")

    X, y = prepare_dataset(df)

    print("Splitting dataset...")

    X_train, X_test, y_train, y_test = train_test_split_time_series(X, y)

    print("Training XGBoost model...")

    model = train_model(X_train, y_train)

    print("Evaluating model...")

    predictions = evaluate_model(model, X_test, y_test)

    show_feature_importance(model, X_train)

    save_model(model)

    print("\nTraining completed.")


if __name__ == "__main__":
    main()