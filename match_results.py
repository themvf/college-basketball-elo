"""
Script to manually match predictions with results
"""
import utils
import prediction_tracker
from datetime import datetime

print("Matching predictions with game results...")

# Load game data
all_games = utils.read_csv('Data/20101101-20251109.csv')

# Filter to games from Nov 5-7, 2025
recent_games = [g for g in all_games if g[5] >= '20251105' and g[5] <= '20251107']

print(f"Found {len(recent_games)} recent games")

# Convert to format for update_results
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

# Update predictions
update_date = datetime.now().strftime('%Y%m%d')
updated_count = prediction_tracker.update_results(results, update_date)

print(f"✓ Updated {updated_count} predictions with results")

# Show summary
db = prediction_tracker.load_database()
played = db[db['game_played'] == 1]

print(f"\nDatabase Status:")
print(f"  Total predictions: {len(db)}")
print(f"  Completed games: {len(played)}")
print(f"  Pending games: {len(db) - len(played)}")

if len(played) > 0:
    correct = played['prediction_correct'].sum()
    accuracy = correct / len(played)
    mean_error = played['spread_error'].mean()
    print(f"\n  Accuracy: {accuracy:.2%} ({correct}/{len(played)})")
    print(f"  Mean spread error: {mean_error:.2f} points")

    print("\n✅ Dashboard is now ready with real data!")
    print("   Refresh your Streamlit dashboard to see the results")
else:
    print("\nℹ️  No matches found - team names may differ between predictions and results")
