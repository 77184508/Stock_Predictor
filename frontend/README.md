# Stock Predictor Frontend

Modern, simple React frontend for the Stock Predictor application.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
The frontend will be available at `http://localhost:5173`

### 3. Build for Production
```bash
npm run build
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── main.jsx              # Entry point
│   ├── App.jsx               # Main app component
│   ├── App.css               # All styling
│   └── components/
│       ├── Dashboard.jsx      # Shows all predictions
│       └── StockDetail.jsx    # Shows single stock details
├── index.html                # HTML template
├── vite.config.js            # Vite configuration
└── package.json              # Dependencies
```

## 🎨 Features

- **Modern Design**: Clean, gradient-based UI with smooth animations
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Real-time Data**: API integration with FastAPI backend
- **Two Views**: Dashboard (all stocks) and Detail (single stock)
- **Easy to Understand**: Plain JSX with helpful comments
- **Error Handling**: Graceful error states and retry buttons

## 🔌 API Integration

The frontend connects to the backend API at `http://localhost:8000`

**Key Endpoints Used:**
- `GET /health` - Check API status
- `GET /stock-symbols` - Get list of tracked stocks
- `GET /predictions?limit=10` - Get latest predictions
- `GET /predictions/{symbol}?limit=30` - Get stock history
- `POST /trigger-dag` - Run prediction pipeline

## 🎯 How It Works

1. **Load Dashboard**: Fetches predictions and symbols on page load
2. **View Predictions**: Grid displays all latest stock predictions
3. **Click Card**: Select a stock to see historical predictions
4. **Run Pipeline**: Click button to trigger Airflow DAG
5. **Auto Refresh**: Data reloads every few seconds

## ⚙️ Dependencies

- **React 18**: UI framework
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API calls

## 🖼️ Component Breakdown

### App.jsx
- Main container
- State management for page routing
- Routes between Dashboard and StockDetail

### Dashboard.jsx
- Grid layout of prediction cards
- Fetch all predictions and symbols
- Trigger pipeline button
- Click to view details

### StockDetail.jsx
- Historical predictions for single stock
- List view of predictions
- Back button to dashboard
- Refresh stock data

## 💡 Tips for Development

- Check browser console (F12) for any errors
- Verify backend is running: `docker ps`
- API should respond on `localhost:8000/health`
- Vite auto-reloads on file changes
- Smooth animations on all interactions

## 📱 Responsive Breakpoints

- **Desktop**: 1200px+ (multi-column grid)
- **Tablet**: 768px-1199px (2-column grid)
- **Mobile**: <768px (single column)

## 🚨 Troubleshooting

**"Failed to load data" error?**
- Check: Backend running on port 8000
- Run: `docker ps` to verify all services
- Try: Refresh page

**API calls taking too long?**
- DAG is still running (takes 2-3 minutes)
- Try: Click refresh button after waiting

**Styling looks broken?**
- Import of App.css might fail
- Try: Clear browser cache (Ctrl+Shift+Delete)

## 📝 Notes

All code is heavily commented to help you learn React!
- Look at component state management (useState)
- See how we fetch API data (useEffect + axios)
- Understand conditional rendering patterns
- Notice responsive grid layout in CSS
