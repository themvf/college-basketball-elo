import streamlit as st
import pandas as pd
import datetime
import glob
import os
import elo
import predictions

# Page configuration
st.set_page_config(
    page_title="College Basketball ELO Predictions",
    page_icon="🏀",
    layout="wide"
)

# Title
st.title("🏀 College Basketball ELO Predictions")
st.markdown("---")

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Select View",
    ["Today's Predictions", "Team Rankings", "Single Game Predictor", "About"]
)

@st.cache_data(ttl=3600)
def get_elo_state(stop_short='99999999'):
    """Load the ELO state with caching"""
    return elo.main(stop_short=stop_short)

@st.cache_data(ttl=3600)
def get_latest_predictions():
    """Get the most recent prediction file"""
    csv_files = glob.glob('Outputs/*.csv')
    if not csv_files:
        return None
    latest_file = max(csv_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    filename = os.path.basename(latest_file)
    return df, filename

@st.cache_data(ttl=3600)
def get_top_teams(n=50):
    """Get top n teams by ELO rating"""
    elo_state = get_elo_state()
    top_teams = elo_state.get_top(n)
    df = pd.DataFrame(top_teams, columns=['Team', 'ELO Rating', '7 Day Change'])
    return df

if page == "Today's Predictions":
    st.header("Today's Game Predictions")

    result = get_latest_predictions()
    if result is None:
        st.warning("No prediction data available. Run predictions.py to generate predictions.")
    else:
        df, filename = result
        st.caption(f"Data from: {filename}")

        # Display predictions
        st.dataframe(
            df,
            width='stretch',
            hide_index=True
        )

        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Games", len(df))
        with col2:
            neutral_games = df[df['Neutral'] == 1].shape[0] if 'Neutral' in df.columns else 0
            st.metric("Neutral Site Games", neutral_games)
        with col3:
            home_games = len(df) - neutral_games
            st.metric("Home Games", home_games)

        # Show some interesting matchups
        st.subheader("Close Matchups (Within 5 Points)")
        if 'Home Pred. Spread' in df.columns:
            close_games = df[abs(df['Home Pred. Spread']) <= 5]
            if len(close_games) > 0:
                st.dataframe(
                    close_games,
                    width='stretch',
                    hide_index=True
                )
            else:
                st.info("No close matchups today")

elif page == "Team Rankings":
    st.header("Current Team Rankings")

    # Slider for number of teams
    num_teams = st.slider("Number of teams to display", min_value=10, max_value=100, value=50, step=10)

    df = get_top_teams(num_teams)

    # Display rankings
    st.dataframe(
        df,
        width='stretch',
        hide_index=True
    )

    # Top 10 highlights
    st.subheader("Top 10 Teams")
    top_10 = df.head(10)

    for idx, row in top_10.iterrows():
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**#{idx + 1} {row['Team']}**")
        with col2:
            st.write(f"ELO: {row['ELO Rating']}")
        with col3:
            change = row['7 Day Change']
            if isinstance(change, str):
                change = change.replace('+', '')
            st.write(f"7d: {change}")

elif page == "Single Game Predictor":
    st.header("Single Game Predictor")
    st.markdown("Predict the outcome of any matchup between two teams")

    # Get list of teams
    elo_state = get_elo_state()
    teams = sorted(list(elo_state.teams.keys()))

    col1, col2 = st.columns(2)

    with col1:
        home_team = st.selectbox("Home Team", teams, index=0 if len(teams) > 0 else None)

    with col2:
        away_team = st.selectbox("Away Team", teams, index=1 if len(teams) > 1 else None)

    neutral_site = st.checkbox("Neutral Site?")

    if st.button("Predict Game", type="primary"):
        if home_team and away_team:
            if home_team == away_team:
                st.error("Please select two different teams")
            else:
                winner, prob, home_spread = predictions.predict_game(
                    elo_state,
                    home_team,
                    away_team,
                    pick_mode=1,
                    neutral=neutral_site
                )

                st.markdown("---")
                st.subheader("Prediction Results")

                # Display matchup
                if neutral_site:
                    st.markdown(f"### {home_team} vs {away_team} (Neutral Site)")
                else:
                    st.markdown(f"### {away_team} @ {home_team}")

                # Display predictions
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Predicted Winner", winner)

                with col2:
                    st.metric("Win Probability", prob)

                with col3:
                    st.metric(f"{home_team} Spread", f"{home_spread:+.1f}")

                # ELO Ratings
                st.markdown("---")
                st.subheader("Team ELO Ratings")

                col1, col2 = st.columns(2)
                with col1:
                    home_elo = elo_state.get_elo(home_team)
                    st.metric(home_team, f"{home_elo:.0f}")

                with col2:
                    away_elo = elo_state.get_elo(away_team)
                    st.metric(away_team, f"{away_elo:.0f}")

elif page == "About":
    st.header("About This App")

    st.markdown("""
    This Streamlit app provides an interactive interface for viewing college basketball predictions
    based on an ELO rating system.

    ### Features

    - **Today's Predictions**: View predicted outcomes for all scheduled games
    - **Team Rankings**: See the top teams ranked by ELO rating
    - **Single Game Predictor**: Predict the outcome of any matchup

    ### ELO Rating System

    The ELO rating system is inspired by FiveThirtyEight's NBA and NFL prediction models.
    It accounts for:

    - Team strength based on historical performance
    - Strength of schedule
    - Home court advantage
    - Margin of victory

    ### Key Parameters

    - **K-Factor**: 47 (controls rating adjustment magnitude)
    - **Home Advantage**: +82 ELO points (~3.3 point spread)
    - **Season Carryover**: 0.64 (regression toward conference average)
    - **ELO to Points**: -24.78 (conversion factor for spreads)

    ### Data Sources

    - Game data: [Scores and Odds](https://www.scoresandodds.com/ncaab)
    - Historical data goes back to the 2010 season

    ### Links

    - [GitHub Repository](https://github.com/grdavis/college-basketball-elo)
    - [Latest Daily Predictions](https://grdavis.github.io/college-basketball-elo/)

    ---

    **Note**: Predictions are for informational purposes only. Please gamble responsibly.
    """)

    # Display system info
    st.subheader("System Information")
    elo_state = get_elo_state()
    st.write(f"**Ratings Current Through**: {elo_state.date}")
    st.write(f"**Total Teams in System**: {len(elo_state.teams)}")
    st.write(f"**Seasons Simulated**: {elo_state.season_count}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("College Basketball ELO Predictions")
st.sidebar.caption("Data updated daily via GitHub Actions")
