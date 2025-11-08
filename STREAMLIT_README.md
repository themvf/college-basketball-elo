# College Basketball ELO Predictions - Streamlit App

This Streamlit app provides an interactive interface for viewing college basketball predictions based on the ELO rating system.

## Features

- **Today's Predictions**: View predicted outcomes for all scheduled games with win probabilities and spreads
- **Team Rankings**: See the top teams ranked by ELO rating with 7-day changes
- **Single Game Predictor**: Predict the outcome of any matchup between two teams
- **About**: Learn more about the ELO rating system and methodology

## Installation

1. Install the required dependencies:
```bash
pip install streamlit
```

Note: The other dependencies (pandas, numpy, etc.) should already be installed from the main `requirements.txt`.

## Running the App

To run the Streamlit app:

```bash
streamlit run app.py
```

This will start a local web server and open the app in your default browser (typically at http://localhost:8501).

## Usage

### Today's Predictions
- View all games scheduled for today with predictions
- See close matchups (within 5 points)
- View neutral site games vs home games

### Team Rankings
- Adjust the slider to show between 10-100 top teams
- View ELO ratings and 7-day changes
- See highlighted top 10 teams

### Single Game Predictor
- Select a home team and away team from dropdowns
- Toggle neutral site option if applicable
- Click "Predict Game" to see:
  - Predicted winner
  - Win probability
  - Point spread
  - Current ELO ratings for both teams

## Data Sources

The app uses:
- Latest prediction CSVs from the `Outputs/` directory
- ELO state calculated from historical game data
- Real-time team rankings

## Notes

- Predictions are cached for 1 hour to improve performance
- The app automatically finds and displays the most recent prediction file
- Teams marked with an asterisk (*) are new to the system and predictions should be taken with caution
- Predictions are for informational purposes only

## Troubleshooting

If you encounter issues:

1. **No predictions showing**: Run `python3 predictions.py` to generate today's predictions
2. **Module not found errors**: Install dependencies with `pip install -r requirements.txt`
3. **Port already in use**: Specify a different port with `streamlit run app.py --server.port 8502`

## Architecture

The app is organized into 4 main pages:
- `app.py` - Main application file with all page logic
- Uses `@st.cache_data` for efficient data loading
- Leverages existing `elo.py` and `predictions.py` modules for calculations
