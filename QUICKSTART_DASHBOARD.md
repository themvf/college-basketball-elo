# Quick Start: Streamlit Dashboard

Get your interactive prediction performance dashboard running in 3 minutes! 🚀

## Prerequisites

- Python 3.7 or higher
- Prediction tracking system already set up (see PREDICTION_TRACKING.md)
- Some prediction data in `Data/predictions_database.csv`

## Installation (One Time)

```bash
# Install Streamlit and dependencies
pip install -r requirements-streamlit.txt
```

That's it! Takes about 30 seconds.

## Running the Dashboard

```bash
# Start the dashboard
streamlit run streamlit_dashboard.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

## First Time Setup

If you see "No prediction data available":

1. **Initialize the database:**
   ```bash
   python prediction_tracker.py init
   ```

2. **Backfill existing predictions:**
   ```bash
   python prediction_tracker.py backfill
   ```

3. **Refresh the dashboard** - Click the refresh button in the sidebar

## What You'll See

The dashboard opens with 6 main sections:

### 1. 📊 Overview Metrics (Top)
5 key performance cards showing:
- Current accuracy percentage
- Brier score (calibration)
- Mean spread error
- Beat Vegas rate
- Last 7 days performance

### 2. 📈 Accuracy Trends
- Rolling accuracy over time
- Rolling Brier score
- Adjust window size with slider

### 3. 📏 Spread Performance
- Error distribution histogram
- Spread error trends

### 4. 🎯 Calibration Analysis
- Calibration curve (predicted vs actual)
- Accuracy by confidence level

### 5. 💰 Vegas Comparison (if available)
- ELO vs Vegas spread errors
- Beat Vegas rate over time

### 6. 🔍 Recent Predictions Table
- Last N games (adjustable)
- Detailed results with ✅/❌ indicators

## Quick Tips

### Sidebar Filters
- **Date Range**: Focus on specific periods
- **Game Type**: Filter Home/Away or Neutral
- **Rolling Window**: Smooth trend charts (5-50 games)
- **Recent Games**: Control table size (10-100)

### Navigation
- Scroll down to see all sections
- Click ⋮ on charts to download/zoom
- Hover over data points for details

### Data Export
At the bottom:
- **CSV Download**: Export filtered predictions
- **JSON Summary**: Get current metrics

### Refresh Data
Click "🔄 Refresh Data" in sidebar after:
- New predictions are made
- New results come in
- Daily GitHub Action runs

## Common Issues

**Dashboard won't start:**
```bash
# Check Streamlit is installed
streamlit --version

# If not, install again
pip install streamlit
```

**No data showing:**
```bash
# Verify database exists
ls Data/predictions_database.csv

# If not, initialize and backfill
python prediction_tracker.py init
python prediction_tracker.py backfill
```

**Want to run on different port:**
```bash
streamlit run streamlit_dashboard.py --server.port 8080
```

**Want others to access (local network):**
```bash
streamlit run streamlit_dashboard.py --server.address 0.0.0.0
```

## Daily Workflow

1. **Morning**: Open dashboard to check overnight results
2. **Filter**: Set date range to "Last 7 days"
3. **Check**: Overview metrics for any drops
4. **Review**: Recent predictions table for accuracy
5. **Export**: Download data if needed for analysis

## Next Steps

- Read full docs: [STREAMLIT_DASHBOARD.md](STREAMLIT_DASHBOARD.md)
- Learn tracking system: [PREDICTION_TRACKING.md](PREDICTION_TRACKING.md)
- Deploy to cloud: See Streamlit Cloud deployment section

## Getting Help

- Full dashboard docs: `STREAMLIT_DASHBOARD.md`
- Tracking system docs: `PREDICTION_TRACKING.md`
- Streamlit docs: https://docs.streamlit.io

---

**You're all set! Enjoy monitoring your predictions! 🏀📊**
