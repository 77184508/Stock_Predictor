CREATE TABLE IF NOT EXISTS stock_prices (
    symbol TEXT,
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    PRIMARY KEY(symbol, date)
);

CREATE TABLE IF NOT EXISTS stock_features (
    symbol TEXT,
    date DATE,
    close FLOAT,
    return_1d FLOAT,
    ma_7 FLOAT,
    ma_21 FLOAT,
    volatility FLOAT,
    lag_1 FLOAT,
    lag_5 FLOAT,
    lag_10 FLOAT,
    momentum FLOAT,
    target_return FLOAT,
    PRIMARY KEY(symbol, date)
);

CREATE TABLE IF NOT EXISTS predictions (
    symbol TEXT,
    date DATE,
    predicted_return FLOAT,
    predicted_price FLOAT,
    model_name TEXT,
    PRIMARY KEY(symbol, date, model_name)
);