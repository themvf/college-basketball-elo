# Prediction Tracking System

This document describes the prediction tracking system that monitors the accuracy of our ELO-based college basketball predictions.

## Overview

The tracking system automatically:
1. **Stores predictions** made each day in a persistent database
2. **Matches predictions** with actual game results
3. **Calculates metrics** to evaluate prediction accuracy
4. **Generates reports** showing model performance over time

## Files Added

### Core Module
- **`prediction_tracker.py`**: Main module for tracking predictions and results
  - `initialize_database()`: Creates the predictions database
  - `store_predictions()`: Saves daily predictions
  - `update_results()`: Matches predictions with actual results
  - `calculate_metrics()`: Computes accuracy statistics
  - `generate_report()`: Creates performance reports
  - `backfill_predictions()`: Imports historical prediction files

### Report Generator
- **`generate_performance_report.py`**: Generates performance metrics and markdown reports
  - Creates `Data/performance_metrics.json` with statistics
  - Creates `docs/performance.md` for GitHub Pages

### Database
- **`Data/predictions_database.csv`**: Persistent storage of all predictions and results
  - Columns: prediction_date, game_date, teams, probabilities, spreads, ELO ratings, actual scores, accuracy metrics

### GitHub Actions
- **`.github/workflows/daily_predictions.yml`** (modified): Now generates performance report after making predictions
- **`.github/workflows/update_performance_tracking.yml`** (new): Weekly job to backfill and update tracking data

## Files Modified

- **`predictions.py`**: Added call to `prediction_tracker.store_predictions()` after generating daily predictions
- **`scraper.py`**: Added call to `prediction_tracker.update_results()` after scraping game results

## How It Works

### Daily Workflow
1. GitHub Action runs at 9 AM EST
2. Scraper gets yesterday's game results → **Updates predictions database with results**
3. ELO ratings are recalculated based on results
4. Predictions are made for today's games → **Stored in predictions database**
5. Performance report is generated with updated statistics
6. All changes committed to repository

### Metrics Tracked

**Accuracy Metrics:**
- Win/Loss Accuracy: % of games predicted correctly
- Brier Score: Measures probability calibration (0.0 = perfect, 0.25 = random)
- Log Loss: Penalizes confident wrong predictions
- Spread Error: Difference between predicted and actual point spreads

**Confidence Stratification:**
- Tracks accuracy at different confidence levels (50-60%, 60-70%, etc.)
- Ensures model is well-calibrated (70% predictions should win 70% of the time)

**Vegas Comparison:**
- Percentage of games where ELO prediction beats Vegas spread
- Identifies potential betting value

**Time-Based Analysis:**
- Overall performance (all time)
- Last 7 days
- Last 30 days

## Usage

### Command Line

Initialize database:
```bash
python prediction_tracker.py init
```

View metrics:
```bash
python prediction_tracker.py metrics
```

Generate report:
```bash
python prediction_tracker.py report
```

Backfill historical predictions:
```bash
python prediction_tracker.py backfill
```

Generate full performance report:
```bash
python generate_performance_report.py
```

### Programmatic

```python
import prediction_tracker

# Initialize
prediction_tracker.initialize_database()

# Store predictions
prediction_tracker.store_predictions(predictions_df, prediction_date, game_date, elo_state)

# Update with results
prediction_tracker.update_results(results_list, update_date)

# Calculate metrics
metrics = prediction_tracker.calculate_metrics()
metrics_7day = prediction_tracker.calculate_metrics(days_back=7)

# Generate report
report_text = prediction_tracker.generate_report(output_file='report.md')
```

## Viewing Results

### GitHub Pages (Static Reports)
Performance reports are automatically published to GitHub Pages:
- **Predictions**: `https://your-username.github.io/college-basketball-elo/`
- **Performance**: `https://your-username.github.io/college-basketball-elo/performance.html`

The performance page shows:
- Overall accuracy statistics
- Recent performance trends
- Confidence-stratified accuracy
- Comparison with Vegas spreads
- Historical metrics

### Streamlit Dashboard (Interactive)
For real-time interactive analysis, use the Streamlit dashboard:

```bash
pip install -r requirements-streamlit.txt
streamlit run streamlit_dashboard.py
```

The dashboard provides:
- **Interactive Charts**: Zoom, pan, and explore data
- **Date Filters**: Focus on specific time periods
- **Rolling Windows**: Adjustable trend analysis
- **Live Updates**: Real-time metrics as data arrives
- **Data Export**: Download filtered data and metrics
- **Calibration Analysis**: Visual probability calibration
- **Vegas Comparison**: Side-by-side performance analysis

See [STREAMLIT_DASHBOARD.md](STREAMLIT_DASHBOARD.md) for full documentation.

## Data Persistence

Unlike the prediction output CSV files (which are cleaned up after 3 days), the predictions database **permanently stores all predictions** enabling:
- Long-term performance analysis
- Season-over-season comparisons
- Model improvement tracking
- Historical accuracy verification

## Troubleshooting

**Database not found:**
Run `python prediction_tracker.py init` to create it.

**No metrics available:**
Predictions need time to be matched with results. After games are played and scraped, run:
```bash
python generate_performance_report.py
```

**Backfilling not working:**
Ensure prediction CSV files exist in the `Outputs/` folder with the naming pattern:
`YYYYMMDD Game Predictions Based on Ratings through YYYYMMDD...csv`

## Future Enhancements

Potential additions:
- Interactive visualization dashboard
- Model drift detection and alerts
- A/B testing framework for parameter variations
- Public API for metrics
- Tournament-specific performance tracking
- Conference-level accuracy breakdown
- Home/Away/Neutral game performance comparison
