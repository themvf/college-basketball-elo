"""
Performance Report Generator
Generates performance metrics and a markdown report for GitHub Pages
"""

import prediction_tracker
import json
import os
import utils

DATA_FOLDER = utils.DATA_FOLDER
DOCS_FOLDER = 'docs'

def generate_full_report():
    """
    Generate a complete performance report with metrics and visualizations
    """
    # Calculate metrics
    overall_metrics = prediction_tracker.calculate_metrics()
    last_7_days = prediction_tracker.calculate_metrics(days_back=7)
    last_30_days = prediction_tracker.calculate_metrics(days_back=30)

    # Save metrics as JSON
    metrics_file = os.path.join(DATA_FOLDER, 'performance_metrics.json')
    with open(metrics_file, 'w') as f:
        json.dump({
            'overall': overall_metrics,
            'last_7_days': last_7_days,
            'last_30_days': last_30_days
        }, f, indent=2, default=int)

    print(f"Saved metrics to {metrics_file}")

    # Generate markdown report
    report = generate_markdown_report(overall_metrics, last_7_days, last_30_days)

    # Save to docs folder for GitHub Pages
    report_file = os.path.join(DOCS_FOLDER, 'performance.md')
    os.makedirs(DOCS_FOLDER, exist_ok=True)

    with open(report_file, 'w') as f:
        f.write(report)

    print(f"Saved performance report to {report_file}")

    # Also print summary to console
    print("\n" + "="*60)
    print("PREDICTION PERFORMANCE SUMMARY")
    print("="*60)

    if overall_metrics.get('total_games_played', 0) > 0:
        print(f"\nOverall Performance:")
        print(f"  Total Predictions: {overall_metrics['total_predictions']}")
        print(f"  Accuracy: {overall_metrics['accuracy']:.2%}")
        print(f"  Brier Score: {overall_metrics['brier_score']:.4f}")
        print(f"  Mean Spread Error: {overall_metrics['mean_spread_error']:.2f} points")

        if last_7_days.get('total_games_played', 0) > 0:
            print(f"\nLast 7 Days:")
            print(f"  Games: {last_7_days['total_predictions']}")
            print(f"  Accuracy: {last_7_days['accuracy']:.2%}")

        if last_30_days.get('total_games_played', 0) > 0:
            print(f"\nLast 30 Days:")
            print(f"  Games: {last_30_days['total_predictions']}")
            print(f"  Accuracy: {last_30_days['accuracy']:.2%}")
    else:
        print("\nNo completed games with predictions yet.")

    print("="*60 + "\n")

def generate_markdown_report(overall, last_7, last_30):
    """
    Generate a markdown report for GitHub Pages
    """
    report = "# ELO Prediction Performance Report\n\n"

    if overall.get('total_games_played', 0) == 0:
        report += "No completed games with predictions yet.\n"
        return report

    report += f"**Last Updated**: {overall['last_updated']}\n\n"
    report += f"**Date Range**: {overall['date_range']['earliest']} to {overall['date_range']['latest']}\n\n"

    # Overall Performance Section
    report += "## Overall Performance\n\n"
    report += "| Metric | Value |\n"
    report += "|--------|-------|\n"
    report += f"| Total Predictions | {overall['total_predictions']} |\n"
    report += f"| Correct Predictions | {overall['correct_predictions']} |\n"
    report += f"| **Accuracy** | **{overall['accuracy']:.2%}** |\n"
    report += f"| Brier Score | {overall['brier_score']:.4f} |\n"
    report += f"| Log Loss | {overall['log_loss']:.4f} |\n"
    report += f"| Mean Spread Error | {overall['mean_spread_error']:.2f} pts |\n"
    report += f"| Median Spread Error | {overall['median_spread_error']:.2f} pts |\n"

    # Recent Performance
    report += "\n## Recent Performance\n\n"
    report += "| Period | Games | Accuracy | Mean Spread Error |\n"
    report += "|--------|-------|----------|-------------------|\n"

    if last_7.get('total_games_played', 0) > 0:
        report += f"| Last 7 Days | {last_7['total_predictions']} | {last_7['accuracy']:.2%} | {last_7['mean_spread_error']:.2f} pts |\n"

    if last_30.get('total_games_played', 0) > 0:
        report += f"| Last 30 Days | {last_30['total_predictions']} | {last_30['accuracy']:.2%} | {last_30['mean_spread_error']:.2f} pts |\n"

    report += f"| All Time | {overall['total_predictions']} | {overall['accuracy']:.2%} | {overall['mean_spread_error']:.2f} pts |\n"

    # Vegas Comparison
    if overall.get('beat_vegas_pct') is not None:
        report += "\n## Performance vs Vegas Spreads\n\n"
        report += "| Metric | Value |\n"
        report += "|--------|-------|\n"
        report += f"| Games with Vegas Spreads | {overall['vegas_comparisons']} |\n"
        report += f"| Beat Vegas Accuracy | {overall['beat_vegas_pct']:.2%} |\n"

    # Confidence Stratification
    report += "\n## Prediction Accuracy by Confidence Level\n\n"
    report += "How accurate are we when we're confident vs uncertain?\n\n"
    report += "| Confidence Range | Games | Accuracy |\n"
    report += "|------------------|-------|----------|\n"

    for conf_range, data in overall['confidence_stratified'].items():
        report += f"| {conf_range} | {data['games']} | {data['accuracy']:.2%} |\n"

    # Interpretation Guide
    report += "\n## Understanding the Metrics\n\n"
    report += "**Accuracy**: Percentage of games where we correctly predicted the winner.\n\n"
    report += "**Brier Score**: Measures the accuracy of probabilistic predictions. "
    report += "Lower is better. Perfect predictions = 0.0, random guessing ≈ 0.25.\n\n"
    report += "**Log Loss**: Measures how well our predicted probabilities match actual outcomes. "
    report += "Lower is better. Perfect predictions = 0.0.\n\n"
    report += "**Spread Error**: Average difference between our predicted point spread and the actual margin of victory.\n\n"
    report += "**Beat Vegas**: Percentage of games where our spread prediction was more accurate than the Vegas spread.\n\n"
    report += "**Confidence Stratified**: When we predict a team has a 70-80% chance to win, "
    report += "they should actually win about 70-80% of the time. This table shows our calibration.\n\n"

    # Link back to predictions
    report += "---\n\n"
    report += "[← Back to Today's Predictions](index.md)\n"

    return report

if __name__ == "__main__":
    generate_full_report()
