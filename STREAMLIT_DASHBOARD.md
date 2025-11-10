# Streamlit Dashboard - Performance Monitoring

A real-time interactive dashboard to monitor and analyze your college basketball ELO prediction performance.

## 🎯 Features

### Overview Metrics
- **Win/Loss Accuracy**: Overall prediction correctness
- **Brier Score**: Probability calibration quality
- **Mean/Median Spread Error**: Point spread accuracy
- **Beat Vegas Rate**: Performance vs Vegas spreads
- **Last 7 Days**: Recent performance snapshot

### Interactive Visualizations

#### 1. Accuracy Trends Over Time
- Rolling accuracy window (adjustable 5-50 games)
- Rolling Brier score trends
- Track model performance changes

#### 2. Spread Performance
- Spread error distribution histogram
- Rolling spread error over time
- Compare predicted vs actual margins

#### 3. Probability Calibration
- **Calibration Curve**: Are 70% predictions correct 70% of the time?
- **Confidence Analysis**: Accuracy by confidence level (50-60%, 60-70%, etc.)
- Visual verification of model calibration

#### 4. Vegas Comparison
- Side-by-side error comparison: ELO vs Vegas
- Beat Vegas rate over time
- Identify when your model has edge

#### 5. Recent Predictions Table
- Sortable/filterable table of recent games
- Shows prediction correctness
- Spread error for each game
- Adjustable number of games (10-100)

### Filters & Settings
- **Date Range Filter**: Focus on specific time periods
- **Game Type Filter**: Home/Away vs Neutral sites
- **Rolling Window**: Adjust smoothing for trend charts
- **Recent Games**: Control table size

### Data Export
- Download filtered data as CSV
- Export summary metrics as JSON
- Full prediction history available

## 🚀 Installation

1. **Install Streamlit dependencies:**
```bash
pip install -r requirements-streamlit.txt
```

This installs:
- `streamlit` - Dashboard framework
- `plotly` - Interactive charts
- `pandas` & `numpy` - Data processing (if not already installed)

2. **Verify installation:**
```bash
streamlit --version
```

## 📊 Running the Dashboard

### Local Development

**Start the dashboard:**
```bash
streamlit run streamlit_dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

### Custom Port/Host

```bash
# Run on specific port
streamlit run streamlit_dashboard.py --server.port 8080

# Allow external access
streamlit run streamlit_dashboard.py --server.address 0.0.0.0
```

### Production Deployment

**Option 1: Streamlit Cloud (Recommended)**
1. Push your repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy `streamlit_dashboard.py`
5. Share the public URL

**Option 2: Docker**
```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
RUN pip install -r requirements-streamlit.txt

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.address", "0.0.0.0"]
```

**Option 3: Heroku, AWS, Google Cloud**
See [Streamlit deployment docs](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

## 🎨 Dashboard Sections

### 1. Overview Cards (Top Row)
Real-time KPIs at a glance:
- Current accuracy percentage
- Brier score (calibration quality)
- Average spread error
- Performance vs Vegas
- Last 7 days trend

### 2. Accuracy Trends
Two charts showing:
- **Left**: Rolling accuracy over time (adjustable window)
- **Right**: Rolling Brier score (lower is better)

Both include reference lines for baselines.

### 3. Spread Performance
Two charts showing:
- **Left**: Distribution of spread errors (histogram)
- **Right**: Rolling mean spread error over time

### 4. Probability Calibration
Two charts showing:
- **Left**: Calibration curve (predicted vs actual win rates)
  - Perfect calibration = diagonal line
  - Bubble size = number of games
- **Right**: Accuracy by confidence bucket (bar chart)

### 5. Vegas Comparison (if data available)
Two charts showing:
- **Left**: Bar comparison of ELO vs Vegas spread errors
- **Right**: Rate of beating Vegas over time

### 6. Recent Predictions Table
Detailed table with:
- Game date
- Final result (scores)
- Predicted winner
- Confidence level
- Predicted spread
- Spread error
- Correctness indicator (✅/❌)

## 🔧 Configuration

### Sidebar Controls

**Date Range Picker:**
- Select start and end dates
- Filters all visualizations
- Defaults to all available data

**Game Type Filter:**
- Home/Away games
- Neutral site games
- Select one or both

**Rolling Window Slider:**
- Adjusts smoothing for time-series charts
- Range: 5-50 games
- Default: 20 games

**Recent Games Slider:**
- Controls table size
- Range: 10-100 games
- Default: 25 games

**Refresh Button:**
- Clears cache and reloads data
- Use after new predictions/results

### Data Updates

The dashboard automatically:
- Caches data for 5 minutes (TTL)
- Reloads when cache expires
- Shows current data timestamp in footer

To force refresh:
- Click "🔄 Refresh Data" in sidebar
- Or press `R` in the browser

## 📈 Interpreting the Metrics

### Accuracy
- **Good**: > 70%
- **Baseline**: 50% (random)
- Higher is always better

### Brier Score
- **Perfect**: 0.0
- **Good**: < 0.15
- **Random**: ~0.25
- Lower is better (measures probability quality)

### Spread Error
- **Excellent**: < 8 points
- **Good**: 8-12 points
- **Baseline**: ~12-15 points
- Measures average prediction error

### Beat Vegas Rate
- **50%**: No advantage
- **> 52%**: Potential edge
- **> 55%**: Strong edge
- Percentage of games where your spread is better

### Calibration
- **Well-calibrated**: Points near diagonal line
- **Over-confident**: Points below diagonal
- **Under-confident**: Points above diagonal

## 🛠 Troubleshooting

**"No prediction data available yet"**
- Database hasn't been initialized
- Run: `python prediction_tracker.py init`

**"No completed games with predictions yet"**
- Predictions exist but no results yet
- Wait for games to be played and scraped
- Or run backfill: `python prediction_tracker.py backfill`

**Dashboard won't start**
- Check Streamlit is installed: `pip install streamlit`
- Verify you're in the correct directory
- Check for port conflicts (try different port)

**Charts not loading**
- Ensure plotly is installed: `pip install plotly`
- Clear cache with refresh button
- Check browser console for errors

**Data not updating**
- Click refresh button
- Restart Streamlit (Ctrl+C then rerun)
- Check predictions_database.csv exists

## 🎯 Best Practices

### Daily Monitoring
1. Check overview metrics each morning
2. Compare 7-day vs all-time accuracy
3. Watch for sudden accuracy drops (model drift)
4. Monitor spread error trends

### Weekly Analysis
1. Review calibration curve
2. Check confidence-stratified accuracy
3. Analyze Vegas comparison trends
4. Export data for deeper analysis

### Season Analysis
1. Adjust date range to specific periods
2. Compare early vs late season performance
3. Analyze conference tournament accuracy
4. Review March Madness predictions

### Performance Alerts
Watch for:
- Accuracy drop below 65% (may need retuning)
- Brier score rising above 0.20 (calibration issues)
- Spread error increasing significantly
- Beat Vegas rate below 48% (losing edge)

## 🔄 Integration with Existing System

The dashboard reads from:
- `Data/predictions_database.csv` - All predictions and results
- Uses `prediction_tracker.py` functions
- Auto-updates as data is added

No configuration needed - works automatically with the tracking system!

## 🚀 Future Enhancements

Potential additions:
- Conference-specific performance breakdown
- Team-level accuracy (which teams are hardest to predict)
- Live game tracking during games
- Email alerts for performance issues
- Comparison with other prediction models
- Tournament bracket simulator with live updates
- Mobile-responsive design improvements

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Chart Gallery](https://plotly.com/python/)
- [Brier Score Explanation](https://en.wikipedia.org/wiki/Brier_score)
- [Calibration Curves](https://scikit-learn.org/stable/modules/calibration.html)

## 💬 Support

If you encounter issues:
1. Check this documentation
2. Review error messages in terminal
3. Verify data files exist
4. Try refreshing the dashboard
5. Restart Streamlit

---

**Happy Analyzing! 🏀📊**
