"""
College Basketball ELO System - Streamlit App
Main entry point for the multi-page application
"""

import streamlit as st

st.set_page_config(
    page_title="College Basketball ELO",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏀 College Basketball ELO Rating System")

st.markdown("""
### Welcome to the College Basketball ELO Prediction System

This application provides comprehensive tools for analyzing college basketball using ELO ratings.

## Available Pages

Use the sidebar to navigate between pages:

### 📊 Team Rankings
View the top ELO-rated teams with their current ratings and recent performance trends.

### 🎯 Game Predictions
See predictions for upcoming games with win probabilities and predicted spreads.

### 🔮 Single Game Predictor
Predict the outcome of any matchup between two teams, including custom scenarios.

### 📈 Prediction Tracking
**NEW!** Monitor prediction accuracy over time with interactive visualizations:
- Overall accuracy and performance metrics
- Calibration analysis
- Performance vs Vegas spreads
- Historical trends and analysis

---

## About the System

Inspired by FiveThirtyEight's approach, this ELO rating system:
- Tracks 300+ college basketball teams since 2010
- Makes daily game predictions
- Accounts for home court advantage and strength of schedule
- Compares predictions against Vegas spreads

### Key Parameters
- **K-factor**: 47 (larger swings than NBA due to greater parity)
- **Home Advantage**: +82 ELO (~3.3 points)
- **Season Carryover**: 0.64 (regresses toward conference average)
- **ELO to Points**: Divide ELO difference by 24.78

## How ELO Works

**ELO ratings** account for strength of schedule. A 22-6 team against tough opponents
may be rated higher than a 14-1 team that played weak competition.

**Win Probability** is calculated from ELO difference:
```
P(win) = 1 / (1 + 10^(-elo_difference/400))
```

**Point Spread** is derived from ELO:
```
Spread = elo_difference / -24.78
```

---

## Getting Started

1. **Check Rankings** - See which teams are currently rated highest
2. **View Predictions** - Look at upcoming game predictions
3. **Make Custom Predictions** - Test hypothetical matchups
4. **Track Performance** - Analyze how accurate the predictions have been

---

**Data Updates**: The system automatically updates daily at 9 AM EST via GitHub Actions.

**Historical Data**: Game logs date back to the start of the 2010 season.

---

Select a page from the sidebar to get started! 🏀
""")

# Display some quick stats in the sidebar
st.sidebar.markdown("---")
st.sidebar.header("Quick Stats")

try:
    import elo
    import prediction_tracker

    # Get latest ELO state
    elo_state = elo.main(stop_short='99999999')
    top_team = elo_state.get_top(1)[0]

    st.sidebar.metric("Top Team", top_team[0], f"{top_team[1]:.0f} ELO")

    # Get prediction stats
    db = prediction_tracker.load_database()
    if len(db) > 0:
        played = db[db['game_played'] == 1]
        if len(played) > 0:
            accuracy = played['prediction_correct'].sum() / len(played)
            st.sidebar.metric("Prediction Accuracy", f"{accuracy:.1%}", f"{len(played)} games")
        else:
            st.sidebar.info(f"{len(db)} predictions stored, awaiting results")

except Exception as e:
    st.sidebar.info("Loading stats...")

st.sidebar.markdown("---")
st.sidebar.markdown("**Navigation** ⬆️")
st.sidebar.markdown("Use the radio buttons above to switch pages")
