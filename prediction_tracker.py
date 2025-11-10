"""
Prediction Tracker Module
Stores predictions and matches them with actual results to track model performance
"""

import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
import utils

DATA_FOLDER = utils.DATA_FOLDER
PREDICTIONS_DB = os.path.join(DATA_FOLDER, 'predictions_database.csv')
METRICS_FILE = os.path.join(DATA_FOLDER, 'performance_metrics.json')

# Database schema columns
DB_COLUMNS = [
    'prediction_date',      # Date prediction was made (YYYYMMDD)
    'game_date',           # Date game is scheduled (YYYYMMDD)
    'neutral',             # 0 or 1
    'home_team',
    'away_team',
    'predicted_home_win_prob',  # 0-1 float
    'predicted_home_spread',    # Negative = home favored
    'predicted_away_spread',    # Negative = away favored
    'vegas_spread',            # Vegas spread for away team
    'home_elo',               # ELO rating at prediction time
    'away_elo',               # ELO rating at prediction time
    'actual_home_score',      # Filled in after game
    'actual_away_score',      # Filled in after game
    'actual_spread',          # Actual away_score - home_score
    'home_won',               # 1 if home won, 0 if away won
    'prediction_correct',     # 1 if predicted winner correctly
    'spread_error',           # abs(predicted_spread - actual_spread)
    'game_played',            # 1 if game happened, 0 if cancelled/postponed
    'result_updated_date'     # Date when results were added
]

def initialize_database():
    """
    Create the predictions database CSV if it doesn't exist
    """
    if not os.path.exists(PREDICTIONS_DB):
        df = pd.DataFrame(columns=DB_COLUMNS)
        df.to_csv(PREDICTIONS_DB, index=False)
        print(f"Created predictions database at {PREDICTIONS_DB}")
    else:
        print(f"Predictions database already exists at {PREDICTIONS_DB}")

def load_database():
    """
    Load the predictions database, creating it if necessary
    """
    if not os.path.exists(PREDICTIONS_DB):
        initialize_database()

    df = pd.read_csv(PREDICTIONS_DB)
    return df

def store_predictions(prediction_df, prediction_date, game_date, elo_state):
    """
    Store daily predictions in the database

    Args:
        prediction_df: DataFrame with columns [Neutral, Away, Away Win Prob., Away Pred. Spread,
                       Live Away Spread, Home, Home Win Prob., Home Pred. Spread]
        prediction_date: Date prediction was made (YYYYMMDD string)
        game_date: Date games are scheduled (YYYYMMDD string)
        elo_state: ELO state object to get team ratings

    Returns:
        Number of predictions stored
    """
    db = load_database()

    new_records = []

    for _, row in prediction_df.iterrows():
        # Extract team names (remove * for non-D1 teams)
        home_team = str(row['Home']).replace('*', '')
        away_team = str(row['Away']).replace('*', '')

        # Parse probabilities (remove % sign and convert to float)
        home_prob_str = str(row['Home Win Prob.']).replace('%', '')
        home_prob = float(home_prob_str) / 100.0 if home_prob_str != 'nan' else None

        # Get ELO ratings
        home_elo = elo_state.get_elo(home_team) if hasattr(elo_state, 'get_elo') else None
        away_elo = elo_state.get_elo(away_team) if hasattr(elo_state, 'get_elo') else None

        # Parse spreads
        home_spread = float(row['Home Pred. Spread']) if pd.notna(row['Home Pred. Spread']) else None
        away_spread = float(row['Away Pred. Spread']) if pd.notna(row['Away Pred. Spread']) else None

        # Parse Vegas spread
        vegas_str = str(row.get('Live Away Spread', 'NL')).strip()
        vegas_spread = None
        if vegas_str not in ['NL', 'nan', '']:
            try:
                vegas_spread = float(vegas_str)
            except:
                vegas_spread = None

        record = {
            'prediction_date': prediction_date,
            'game_date': game_date,
            'neutral': int(row['Neutral']),
            'home_team': home_team,
            'away_team': away_team,
            'predicted_home_win_prob': home_prob,
            'predicted_home_spread': home_spread,
            'predicted_away_spread': away_spread,
            'vegas_spread': vegas_spread,
            'home_elo': home_elo,
            'away_elo': away_elo,
            'actual_home_score': None,
            'actual_away_score': None,
            'actual_spread': None,
            'home_won': None,
            'prediction_correct': None,
            'spread_error': None,
            'game_played': 0,  # Default to not played yet
            'result_updated_date': None
        }

        new_records.append(record)

    # Append to database
    new_df = pd.DataFrame(new_records)
    db = pd.concat([db, new_df], ignore_index=True)

    # Remove duplicates (keep most recent prediction for same game)
    db = db.drop_duplicates(subset=['game_date', 'home_team', 'away_team'], keep='last')

    db.to_csv(PREDICTIONS_DB, index=False)

    print(f"Stored {len(new_records)} predictions for {game_date}")
    return len(new_records)

def normalize_team_name(name):
    """
    Normalize team names for matching (remove special characters, lowercase, etc.)
    """
    if pd.isna(name):
        return ""

    name = str(name).strip()
    # Remove asterisks for non-D1 teams
    name = name.replace('*', '')
    # Remove parentheses content
    name = name.split('(')[0].strip()
    return name

def update_results(results_df, update_date=None):
    """
    Match game results with predictions and update the database

    Args:
        results_df: DataFrame with columns [neutral, away_team, away_score, home_team, home_score, date, away_spread]
                   Can also be a list of games from the main data file
        update_date: Date when results are being updated (YYYYMMDD string), defaults to today

    Returns:
        Number of predictions updated
    """
    if update_date is None:
        update_date = datetime.now().strftime('%Y%m%d')

    db = load_database()

    # If empty database, nothing to update
    if len(db) == 0:
        print("Database is empty, no predictions to update")
        return 0

    updated_count = 0

    # Convert results to list of dicts if it's a DataFrame
    if isinstance(results_df, pd.DataFrame):
        results = results_df.to_dict('records')
    else:
        results = results_df

    for result in results:
        # Parse result
        if isinstance(result, dict):
            neutral = result.get('neutral', 0)
            away_team = normalize_team_name(result.get('away_team', ''))
            away_score = result.get('away_score')
            home_team = normalize_team_name(result.get('home_team', ''))
            home_score = result.get('home_score')
            game_date = str(result.get('date', ''))
        else:
            # Assume it's a list/tuple format from CSV
            neutral = result[0]
            away_team = normalize_team_name(result[1])
            away_score = result[2]
            home_team = normalize_team_name(result[3])
            home_score = result[4]
            game_date = str(result[5])

        # Find matching prediction(s) in database
        # Match on game_date, home_team, away_team
        mask = (
            (db['game_date'] == game_date) &
            (db['home_team'].apply(normalize_team_name) == home_team) &
            (db['away_team'].apply(normalize_team_name) == away_team) &
            (db['game_played'] == 0)  # Only update games not yet marked as played
        )

        matching_indices = db[mask].index

        if len(matching_indices) > 0:
            # Update all matching predictions (there should usually only be one)
            for idx in matching_indices:
                db.at[idx, 'actual_home_score'] = int(home_score)
                db.at[idx, 'actual_away_score'] = int(away_score)
                db.at[idx, 'actual_spread'] = int(away_score) - int(home_score)
                db.at[idx, 'home_won'] = 1 if int(home_score) > int(away_score) else 0

                # Check if prediction was correct
                predicted_home_prob = db.at[idx, 'predicted_home_win_prob']
                if pd.notna(predicted_home_prob):
                    predicted_home_win = predicted_home_prob > 0.5
                    actual_home_win = int(home_score) > int(away_score)
                    db.at[idx, 'prediction_correct'] = 1 if predicted_home_win == actual_home_win else 0

                # Calculate spread error
                predicted_spread = db.at[idx, 'predicted_away_spread']
                if pd.notna(predicted_spread):
                    actual_spread = int(away_score) - int(home_score)
                    db.at[idx, 'spread_error'] = abs(predicted_spread - actual_spread)

                db.at[idx, 'game_played'] = 1
                db.at[idx, 'result_updated_date'] = update_date

                updated_count += 1

    # Save updated database
    db.to_csv(PREDICTIONS_DB, index=False)

    print(f"Updated {updated_count} predictions with results")
    return updated_count

def calculate_metrics(days_back=None, min_date=None):
    """
    Calculate performance metrics from the database

    Args:
        days_back: Only consider games from the last N days
        min_date: Only consider games from this date forward (YYYYMMDD string)

    Returns:
        Dictionary of metrics
    """
    db = load_database()

    # Filter to only games that have been played
    played = db[db['game_played'] == 1].copy()

    if len(played) == 0:
        return {
            'total_predictions': 0,
            'total_games_played': 0,
            'message': 'No completed games with predictions yet'
        }

    # Apply date filters
    if days_back:
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y%m%d')
        played = played[played['game_date'] >= cutoff_date]

    if min_date:
        played = played[played['game_date'] >= min_date]

    if len(played) == 0:
        return {
            'total_predictions': 0,
            'total_games_played': 0,
            'message': 'No games in specified date range'
        }

    # Basic accuracy metrics
    total_games = len(played)
    correct_predictions = played['prediction_correct'].sum()
    accuracy = correct_predictions / total_games if total_games > 0 else 0

    # Brier score (measures probability calibration)
    # Brier = mean((predicted_prob - actual_outcome)^2)
    played['brier_score'] = (played['predicted_home_win_prob'] - played['home_won']) ** 2
    brier_score = played['brier_score'].mean()

    # Log loss
    # LogLoss = -mean(actual * log(predicted) + (1-actual) * log(1-predicted))
    epsilon = 1e-15  # Prevent log(0)
    played['log_loss_term'] = -(
        played['home_won'] * np.log(played['predicted_home_win_prob'].clip(epsilon, 1-epsilon)) +
        (1 - played['home_won']) * np.log((1 - played['predicted_home_win_prob']).clip(epsilon, 1-epsilon))
    )
    log_loss = played['log_loss_term'].mean()

    # Spread metrics
    mean_spread_error = played['spread_error'].mean()
    median_spread_error = played['spread_error'].median()

    # Against the spread (vs Vegas)
    vegas_available = played[played['vegas_spread'].notna()]
    if len(vegas_available) > 0:
        # Did we predict the spread better than Vegas?
        vegas_available['beat_vegas'] = vegas_available['spread_error'] < abs(vegas_available['actual_spread'] - vegas_available['vegas_spread'])
        beat_vegas_pct = vegas_available['beat_vegas'].sum() / len(vegas_available)
    else:
        beat_vegas_pct = None

    # Confidence stratification
    confidence_bins = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    confidence_metrics = {}

    for i in range(len(confidence_bins) - 1):
        lower = confidence_bins[i]
        upper = confidence_bins[i + 1]

        # Games where home team was predicted with probability in this range
        home_conf = played[(played['predicted_home_win_prob'] > lower) &
                          (played['predicted_home_win_prob'] <= upper)]

        # Games where away team was predicted with probability in this range
        away_conf = played[(played['predicted_home_win_prob'] < (1-lower)) &
                          (played['predicted_home_win_prob'] >= (1-upper))]

        conf_games = pd.concat([home_conf, away_conf])

        if len(conf_games) > 0:
            conf_accuracy = conf_games['prediction_correct'].sum() / len(conf_games)
            confidence_metrics[f'{int(lower*100)}-{int(upper*100)}%'] = {
                'games': len(conf_games),
                'accuracy': round(conf_accuracy, 4)
            }

    metrics = {
        'total_predictions': int(total_games),
        'total_games_played': int(total_games),
        'correct_predictions': int(correct_predictions),
        'accuracy': round(accuracy, 4),
        'brier_score': round(brier_score, 4),
        'log_loss': round(log_loss, 4),
        'mean_spread_error': round(mean_spread_error, 2),
        'median_spread_error': round(median_spread_error, 2),
        'beat_vegas_pct': round(beat_vegas_pct, 4) if beat_vegas_pct is not None else None,
        'vegas_comparisons': int(len(vegas_available)),
        'confidence_stratified': confidence_metrics,
        'date_range': {
            'earliest': played['game_date'].min(),
            'latest': played['game_date'].max()
        },
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return metrics

def generate_report(output_file=None):
    """
    Generate a human-readable performance report

    Args:
        output_file: Path to save markdown report (optional)

    Returns:
        String containing markdown report
    """
    metrics = calculate_metrics()

    if metrics.get('total_games_played', 0) == 0:
        report = "# Prediction Performance Report\n\n"
        report += "No completed games with predictions yet.\n"
        return report

    report = "# Prediction Performance Report\n\n"
    report += f"**Generated**: {metrics['last_updated']}\n\n"
    report += f"**Date Range**: {metrics['date_range']['earliest']} to {metrics['date_range']['latest']}\n\n"

    report += "## Overall Performance\n\n"
    report += f"- **Total Predictions**: {metrics['total_predictions']}\n"
    report += f"- **Correct Predictions**: {metrics['correct_predictions']}\n"
    report += f"- **Accuracy**: {metrics['accuracy']:.2%}\n"
    report += f"- **Brier Score**: {metrics['brier_score']:.4f} (lower is better)\n"
    report += f"- **Log Loss**: {metrics['log_loss']:.4f} (lower is better)\n\n"

    report += "## Spread Performance\n\n"
    report += f"- **Mean Spread Error**: {metrics['mean_spread_error']:.2f} points\n"
    report += f"- **Median Spread Error**: {metrics['median_spread_error']:.2f} points\n\n"

    if metrics['beat_vegas_pct'] is not None:
        report += "## vs Vegas Spreads\n\n"
        report += f"- **Games with Vegas Spreads**: {metrics['vegas_comparisons']}\n"
        report += f"- **Beat Vegas Accuracy**: {metrics['beat_vegas_pct']:.2%}\n\n"

    report += "## Confidence Stratified Accuracy\n\n"
    report += "| Confidence Range | Games | Accuracy |\n"
    report += "|-----------------|-------|----------|\n"
    for conf_range, data in metrics['confidence_stratified'].items():
        report += f"| {conf_range} | {data['games']} | {data['accuracy']:.2%} |\n"

    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Report saved to {output_file}")

    return report

def backfill_predictions(outputs_folder='Outputs', elo_state=None):
    """
    Backfill the database with existing prediction CSV files

    Args:
        outputs_folder: Path to folder containing prediction CSV files
        elo_state: Optional ELO state object (if not provided, will use None for ELO ratings)

    Returns:
        Number of predictions backfilled
    """
    import glob
    import re

    prediction_files = glob.glob(os.path.join(outputs_folder, '*Game Predictions*.csv'))

    total_stored = 0

    for file_path in prediction_files:
        try:
            # Extract dates from filename
            # Format: "YYYYMMDD Game Predictions Based on Ratings through YYYYMMDD with Spreads..."
            filename = os.path.basename(file_path)
            match = re.search(r'^(\d{8})', filename)

            if match:
                game_date = match.group(1)
                # Prediction date is usually the same as game date (made in the morning)
                prediction_date = game_date

                # Read prediction file
                df = pd.read_csv(file_path)

                # Store in database
                count = store_predictions(df, prediction_date, game_date, elo_state)
                total_stored += count
                print(f"Backfilled {count} predictions from {filename}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"\nTotal predictions backfilled: {total_stored}")
    return total_stored

if __name__ == "__main__":
    # Command line interface for testing
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'init':
            initialize_database()

        elif command == 'metrics':
            metrics = calculate_metrics()
            import json
            print(json.dumps(metrics, indent=2))

        elif command == 'report':
            report = generate_report()
            print(report)

        elif command == 'backfill':
            backfill_predictions()

        else:
            print("Unknown command. Available: init, metrics, report, backfill")

    else:
        print("Prediction Tracker Module")
        print("Usage: python prediction_tracker.py [init|metrics|report|backfill]")
