import { useState, useEffect } from 'react'
import axios from 'axios'

/**
 * Dashboard Component
 * Shows all available stock predictions in a grid
 * Main page when user opens the app
 */
export default function Dashboard({ onSelectStock }) {
  // State to store all stock predictions
  const [predictions, setPredictions] = useState([])
  
  // State to store available stock symbols
  const [stocks, setStocks] = useState([])
  
  // Track if we're loading data
  const [loading, setLoading] = useState(true)
  
  // Track any errors
  const [error, setError] = useState(null)

  // API base URL - change this to match your backend
  const API_BASE_URL = 'http://localhost:8000'

  /**
   * Load all data when component mounts
   * useEffect with empty dependency = runs once on first render
   */
  useEffect(() => {
    fetchData()
  }, []) // Empty array means: run once

  /**
   * Fetch predictions and stocks from API
   */
  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Get all predictions for dashboard
      const predictionsRes = await axios.get(`${API_BASE_URL}/predictions?limit=10`)
      // API returns { status, count, predictions }
      setPredictions(predictionsRes.data.predictions || [])
      
      // Get list of available stock symbols
      const stocksRes = await axios.get(`${API_BASE_URL}/stock-symbols`)
      setStocks(stocksRes.data.symbols || [])
      
    } catch (err) {
      console.error('Error fetching data:', err)
      setError('Failed to load data. Make sure the backend is running!')
    } finally {
      setLoading(false)
    }
  }

  /**
   * Trigger the Airflow DAG to run predictions
   */
  const handleTriggerPipeline = async () => {
    try {
      setLoading(true)
      await axios.post(`${API_BASE_URL}/trigger-dag`)
      
      // Show success message
      alert('Pipeline triggered! It will take a few minutes...')
      
      // Reload data after a delay
      setTimeout(() => {
        fetchData()
      }, 3000)
      
    } catch (err) {
      console.error('Error triggering pipeline:', err)
      alert('Failed to trigger pipeline!')
      setLoading(false)
    }
  }

  // Show loading state
  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Loading predictions...</div>
      </div>
    )
  }

  // Show error state
  if (error) {
    return (
      <div className="dashboard">
        <div className="error">{error}</div>
        <button onClick={fetchData} className="retry-btn">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="dashboard">
      {/* Control Bar */}
      <div className="dashboard-controls">
        <button 
          onClick={handleTriggerPipeline}
          className="trigger-btn"
        >
          ▶️ Run Prediction Pipeline
        </button>
        <button 
          onClick={fetchData}
          className="refresh-btn"
        >
          🔄 Refresh Data
        </button>
      </div>

      {/* Stock Information */}
      <div className="dashboard-info">
        <p>📊 Tracked Stocks: {stocks.join(', ')}</p>
      </div>

      {/* Predictions Grid */}
      <div className="predictions-grid">
        {predictions.length === 0 ? (
          <div className="no-predictions">
            No predictions yet. Click "Run Pipeline" to start!
          </div>
        ) : (
          predictions.map((pred) => (
            <div 
              key={pred.id}
              className="prediction-card"
              onClick={() => onSelectStock(pred.symbol)}
            >
              <div className="card-header">
                <h3 className="stock-symbol">{pred.symbol}</h3>
                <span className="card-date">
                  {new Date(pred.date).toLocaleDateString()}
                </span>
              </div>

              <div className="card-body">
                <div className="price-info">
                  <div className="info-item">
                    <label>Predicted Price</label>
                    <span className="price">
                      ${pred.predicted_price?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                  <div className="info-item">
                    <label>Expected Return</label>
                    <span className={`return ${pred.predicted_return >= 0 ? 'positive' : 'negative'}`}>
                      {pred.predicted_return?.toFixed(2) || 'N/A'}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="card-footer">
                <span className="click-hint">Click to view details →</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
