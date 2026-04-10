import { useState, useEffect } from 'react'
import axios from 'axios'

/**
 * StockDetail Component
 * Shows detailed information about a specific stock
 * User navigates here by clicking a prediction card
 */
export default function StockDetail({ symbol, onBack }) {
  // State to store predictions for this stock
  const [predictions, setPredictions] = useState([])
  
  // Track if we're loading
  const [loading, setLoading] = useState(true)
  
  // Track any errors
  const [error, setError] = useState(null)

  // API base URL
  const API_BASE_URL = 'http://localhost:8000'

  /**
   * Load stock details when component mounts or symbol changes
   */
  useEffect(() => {
    fetchStockDetails()
  }, [symbol])

  /**
   * Fetch detailed predictions for this stock
   */
  const fetchStockDetails = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Get last 30 predictions for this stock
      const res = await axios.get(
        `${API_BASE_URL}/predictions/${symbol}?limit=30`
      )
      setPredictions(res.data)
    } catch (err) {
      console.error('Error fetching stock details:', err)
      setError('Failed to load stock details')
    } finally {
      setLoading(false)
    }
  }

  // Show loading state
  if (loading) {
    return (
      <div className="stock-detail">
        <button onClick={onBack} className="back-btn">
          ← Back to Dashboard
        </button>
        <div className="loading">Loading {symbol} details...</div>
      </div>
    )
  }

  // Show error state
  if (error) {
    return (
      <div className="stock-detail">
        <button onClick={onBack} className="back-btn">
          ← Back to Dashboard
        </button>
        <div className="error">{error}</div>
        <button onClick={fetchStockDetails} className="retry-btn">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="stock-detail">
      {/* Back Button */}
      <button onClick={onBack} className="back-btn">
        ← Back to Dashboard
      </button>

      {/* Title */}
      <div className="detail-header">
        <h2 className="detail-title">{symbol} - Price Predictions</h2>
        <p className="detail-subtitle">Last 30 predictions</p>
      </div>

      {/* Predictions List or Empty State */}
      {predictions.length === 0 ? (
        <div className="empty-state">
          <p>No predictions available for {symbol}</p>
        </div>
      ) : (
        <div className="predictions-list">
          {predictions.map((pred, index) => (
            <div key={index} className="prediction-row">
              <div className="row-date">
                {new Date(pred.date).toLocaleDateString()}
              </div>
              
              <div className="row-price">
                <label>Price:</label>
                <span>${pred.predicted_price?.toFixed(2) || 'N/A'}</span>
              </div>
              
              <div className="row-return">
                <label>Return:</label>
                <span className={pred.predicted_return >= 0 ? 'positive' : 'negative'}>
                  {pred.predicted_return?.toFixed(2) || 'N/A'}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Refresh Button */}
      <div className="detail-footer">
        <button onClick={fetchStockDetails} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>
    </div>
  )
}
