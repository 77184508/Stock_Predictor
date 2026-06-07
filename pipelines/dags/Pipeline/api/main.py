from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import requests
from database.db_connection import get_connection
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Stock Predictor API", version="1.0.0")

# Airflow config
AIRFLOW_BASE_URL = os.getenv("AIRFLOW_BASE_URL", "http://localhost:8081")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "airflow")
DAG_ID = "stock_pipeline_dag"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Pydantic models
class PredictionResponse(BaseModel):
    symbol: str
    date: str
    predicted_return: float
    predicted_price: float
    model_name: str


class DagTriggerResponse(BaseModel):
    message: str
    dag_id: str
    run_id: Optional[str] = None


class PredictionsListResponse(BaseModel):
    status: str
    count: int
    predictions: List[PredictionResponse]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/trigger-dag", response_model=DagTriggerResponse)
async def trigger_dag():
    """
    Trigger the stock pipeline DAG execution.
    Airflow must be running and accessible.
    """
    try:
        url = f"{AIRFLOW_BASE_URL}/api/v1/dags/{DAG_ID}/dagRuns"
        
        payload = {
            "conf": {},
            "note": f"Triggered via API at {datetime.now().isoformat()}"
        }
        
        response = requests.post(
            url,
            json=payload,
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            return DagTriggerResponse(
                message="DAG triggered successfully",
                dag_id=DAG_ID,
                run_id=data.get("dag_run_id")
            )
        else:
            logger.error(f"Airflow error: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to trigger DAG: {response.text}"
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Airflow service is not available. Ensure it's running."
        )
    except Exception as e:
        logger.error(f"Error triggering DAG: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error triggering DAG: {str(e)}"
        )


@app.get("/predictions", response_model=PredictionsListResponse)
async def get_all_predictions(limit: int = 100):
    """
    Fetch latest predictions for all stocks.
    Returns most recent predictions (latest dates first).
    """
    try:
        conn = get_connection(do_schema=False)
        if conn is None:
            raise HTTPException(
                status_code=503,
                detail="Database connection failed"
            )
        
        cursor = conn.cursor()
        query = """
        SELECT symbol, date, predicted_return, predicted_price, model_name
        FROM predictions
        ORDER BY date DESC, symbol ASC
        LIMIT %s
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        predictions = [
            PredictionResponse(
                symbol=row[0],
                date=str(row[1]),
                predicted_return=float(row[2]),
                predicted_price=float(row[3]),
                model_name=row[4]
            )
            for row in rows
        ]
        
        return PredictionsListResponse(
            status="success",
            count=len(predictions),
            predictions=predictions
        )
    except Exception as e:
        logger.error(f"Error fetching predictions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching predictions: {str(e)}"
        )


@app.get("/predictions/{symbol}", response_model=List[PredictionResponse])
async def get_symbol_predictions(symbol: str, limit: int = 30):
    """
    Fetch predictions for a specific stock symbol.
    Returns most recent predictions first.
    """
    try:
        conn = get_connection(do_schema=False)
        if conn is None:
            raise HTTPException(
                status_code=503,
                detail="Database connection failed"
            )
        
        cursor = conn.cursor()
        query = """
        SELECT symbol, date, predicted_return, predicted_price, model_name
        FROM predictions
        WHERE symbol = %s
        ORDER BY date DESC
        LIMIT %s
        """
        cursor.execute(query, (symbol.upper(), limit))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No predictions found for symbol: {symbol}"
            )
        
        predictions = [
            PredictionResponse(
                symbol=row[0],
                date=str(row[1]),
                predicted_return=float(row[2]),
                predicted_price=float(row[3]),
                model_name=row[4]
            )
            for row in rows
        ]
        
        return predictions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching predictions for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching predictions: {str(e)}"
        )


@app.get("/latest-prediction/{symbol}")
async def get_latest_prediction(symbol: str):
    """
    Get the single most recent prediction for a stock symbol.
    Useful for frontend to show "tomorrow's predicted price".
    """
    try:
        conn = get_connection(do_schema=False)
        if conn is None:
            raise HTTPException(
                status_code=503,
                detail="Database connection failed"
            )
        
        cursor = conn.cursor()
        query = """
        SELECT symbol, date, predicted_return, predicted_price, model_name
        FROM predictions
        WHERE symbol = %s
        ORDER BY date DESC
        LIMIT 1
        """
        cursor.execute(query, (symbol.upper(),))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"No prediction found for symbol: {symbol}"
            )
        
        return PredictionResponse(
            symbol=row[0],
            date=str(row[1]),
            predicted_return=float(row[2]),
            predicted_price=float(row[3]),
            model_name=row[4]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest prediction for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching latest prediction: {str(e)}"
        )


@app.get("/stock-symbols")
async def get_stock_symbols():
    """
    Return configured stock symbols that are tracked.
    """
    try:
        from config.config import STOCK_SYMBOLS
        return {
            "status": "success",
            "count": len(STOCK_SYMBOLS),
            "symbols": STOCK_SYMBOLS
        }
    except Exception as e:
        logger.error(f"Error fetching symbols: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching symbols: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
