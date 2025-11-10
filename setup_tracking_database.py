"""
Setup script to initialize and populate the predictions database
"""
import sys
import os
import pandas as pd
import prediction_tracker
import elo
import utils
import glob
import re
from datetime import datetime

print("=" * 60)
print("PREDICTION TRACKING DATABASE SETUP")
print("=" * 60)

# Step 1: Initialize database
print("\n[1/4] Initializing database...")
prediction_tracker.initialize_database()

# Step 2: Backfill predictions from Outputs folder
print("\n[2/4] Backfilling predictions from Outputs folder...")

# Get ELO state for ratings
print("   Loading ELO state...")
elo_state = elo.main(stop_short='99999999')

# Find all prediction files
prediction_files = sorted(glob.glob('Outputs/*Game Predictions*.csv'))
print(f"   Found {len(prediction_files)} prediction files")

total_stored = 0
for file_path in prediction_files:
    try:
        filename = os.path.basename(file_path)
        # Extract game date from filename (YYYYMMDD at start)
        match = re.search(r'^(\d{8})', filename)

        if match:
            game_date = match.group(1)
            prediction_date = game_date  # Assume prediction made same day

            # Read prediction file
            df = pd.read_csv(file_path)

            # Store in database
            count = prediction_tracker.store_predictions(df, prediction_date, game_date, elo_state)
            total_stored += count
            print(f"   ✓ Stored {count} predictions from {game_date}")

    except Exception as e:
        print(f"   ✗ Error processing {filename}: {e}")

print(f"\n   Total predictions stored: {total_stored}")

# Step 3: Load game results and match with predictions
print("\n[3/4] Matching predictions with actual results...")

# Find latest game data file
data_files = glob.glob('Data/*.csv')
data_files = [f for f in data_files if 'predictions_database' not in f and 'performance_metrics' not in f]
data_files = [f for f in data_files if re.match(r'.*\d{8}-\d{8}\.csv$', f)]

if data_files:
    latest_file = max(data_files, key=os.path.getmtime)
    print(f"   Reading game data from {os.path.basename(latest_file)}")

    # Read all games
    all_games = utils.read_csv(latest_file)

    # Filter to recent games (same dates as predictions)
    # Get date range from predictions
    db = prediction_tracker.load_database()
    if len(db) > 0:
        min_pred_date = str(db['game_date'].min())
        recent_games = [g for g in all_games if str(g[5]) >= min_pred_date]
        print(f"   Found {len(recent_games)} games to match (from {min_pred_date} onwards)")

        # Convert to format expected by update_results
        results = []
        for game in recent_games:
            results.append({
                'neutral': game[0],
                'away_team': game[1],
                'away_score': game[2],
                'home_team': game[3],
                'home_score': game[4],
                'date': game[5]
            })

        # Update predictions database
        update_date = datetime.now().strftime('%Y%m%d')
        updated_count = prediction_tracker.update_results(results, update_date)
        print(f"   ✓ Updated {updated_count} predictions with results")
    else:
        print("   ✗ No predictions to update")
else:
    print("   ✗ No game data files found")

# Step 4: Generate initial performance report
print("\n[4/4] Generating performance report...")
try:
    import generate_performance_report
    generate_performance_report.generate_full_report()
    print("   ✓ Performance report generated")
except Exception as e:
    print(f"   Note: Could not generate report: {e}")

# Show summary
print("\n" + "=" * 60)
print("SETUP COMPLETE!")
print("=" * 60)

# Display quick stats
db = prediction_tracker.load_database()
played = db[db['game_played'] == 1]

print(f"\nDatabase Statistics:")
print(f"  Total predictions: {len(db)}")
print(f"  Completed games: {len(played)}")
print(f"  Pending games: {len(db) - len(played)}")

if len(played) > 0:
    accuracy = played['prediction_correct'].sum() / len(played)
    print(f"\n  Overall accuracy: {accuracy:.2%}")
    print(f"  Mean spread error: {played['spread_error'].mean():.2f} points")

print("\n✅ Your Streamlit dashboard is ready!")
print("   Run: streamlit run streamlit_dashboard.py")
print("\n" + "=" * 60)
