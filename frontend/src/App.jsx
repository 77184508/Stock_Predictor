import { useState } from 'react'
import Dashboard from './components/Dashboard'
import StockDetail from './components/StockDetail'

/**
 * Main App Component
 * Manages page state (dashboard vs detail view)
 * Routes between Dashboard and individual stock details
 */
export default function App() {
  // Track which page we're on: 'dashboard' or 'detail'
  const [currentPage, setCurrentPage] = useState('dashboard')
  
  // Track which stock was selected to show details
  const [selectedSymbol, setSelectedSymbol] = useState(null)

  /**
   * Handle stock selection
   * User clicked on a stock card, show its details
   */
  const handleSelectStock = (symbol) => {
    setSelectedSymbol(symbol)
    setCurrentPage('detail')
  }

  /**
   * Handle going back to dashboard
   */
  const handleBackToDashboard = () => {
    setCurrentPage('dashboard')
    setSelectedSymbol(null)
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <h1 className="app-title">📈 Stock Predictor</h1>
        <p className="app-subtitle">ML-Powered Stock Price Predictions</p>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {/* Show Dashboard if on dashboard page */}
        {currentPage === 'dashboard' && (
          <Dashboard onSelectStock={handleSelectStock} />
        )}

        {/* Show Details if viewing a specific stock */}
        {currentPage === 'detail' && selectedSymbol && (
          <StockDetail 
            symbol={selectedSymbol}
            onBack={handleBackToDashboard}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Real-time stock market predictions powered by machine learning</p>
      </footer>
    </div>
  )
}
