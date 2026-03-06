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