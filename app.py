import streamlit as st
import elo
import predictions
import pandas as pd
import datetime
import utils

# Page configuration
st.set_page_config(
    page_title="College Basketball ELO",
    page_icon="🏀",
    layout="wide"
)

# Title and description
st.title("🏀 College Basketball ELO Ratings & Predictions")
st.markdown("""
This app uses an ELO rating system to rank NCAA Men's College Basketball teams and make predictions.
Inspired by FiveThirtyEight's methodology, adapted for college basketball.
""")

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Select a page",
    ["Team Rankings", "Game Predictions", "Single Game Predictor"]
)

# Initialize ELO state (cached to avoid recomputation)
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_elo_state(stop_short='99999999'):
    """Load and cache the ELO simulation state"""
    return elo.main(stop_short=stop_short)

if page == "Team Rankings":
    st.header("📊 Team Rankings")

    col1, col2 = st.columns(2)

    with col1:
        num_teams = st.number_input(
            "Number of top teams to display",
            min_value=5,
            max_value=100,
            value=25,
            step=5
        )

    with col2:
        use_historical = st.checkbox("View historical rankings")
        historical_date = None
        if use_historical:
            historical_date = st.date_input(
                "Select date",
                value=datetime.date.today() - datetime.timedelta(days=7),
                min_value=datetime.date(2010, 11, 1),
                max_value=datetime.date.today()
            )

    period = st.slider(
        "Days to show rating change",
        min_value=1,
        max_value=30,
        value=7
    )

    if st.button("Get Rankings", type="primary"):
        with st.spinner("Calculating ELO ratings..."):
            stop_short = historical_date.strftime('%Y%m%d') if use_historical else '99999999'
            elo_state = get_elo_state(stop_short)

            # Get top teams
            top_teams = elo_state.get_top(num_teams)

            # Create DataFrame
            df = pd.DataFrame(top_teams, columns=['Team', 'ELO Rating', f'{period} Day Change'])

            # Calculate point spread vs next rank
            spreads = []
            for i in range(len(df) - 1):
                spread = (df.iloc[i]['ELO Rating'] - df.iloc[i+1]['ELO Rating']) / elo.ELO_TO_POINTS_FACTOR
                spreads.append(f"{spread:+.1f}")
            spreads.append('')

            df['Point Spread vs. Next Rank'] = spreads
            df.insert(0, 'Rank', range(1, num_teams + 1))

            st.success(f"Ratings through {elo_state.date}")

            # Display table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn(format="%d"),
                    "ELO Rating": st.column_config.NumberColumn(format="%.0f"),
                }
            )

elif page == "Game Predictions":
    st.header("🎯 Daily Game Predictions")

    forecast_date = st.date_input(
        "Select date for predictions",
        value=datetime.date.today(),
        min_value=datetime.date.today() - datetime.timedelta(days=365),
        max_value=datetime.date.today() + datetime.timedelta(days=30)
    )

    use_historical_data = st.checkbox("Use historical ELO ratings (stop at a specific date)")
    stop_short = '99999999'
    if use_historical_data:
        stop_date = st.date_input(
            "Calculate ratings through this date",
            value=forecast_date - datetime.timedelta(days=1),
            min_value=datetime.date(2010, 11, 1),
            max_value=datetime.date.today()
        )
        stop_short = stop_date.strftime('%Y%m%d')

    if st.button("Get Predictions", type="primary"):
        with st.spinner("Loading ELO ratings and fetching games..."):
            try:
                elo_state = get_elo_state(stop_short)

                # Import scraper functions
                import scraper
                scraper.scrape_neutral_data()
                games = scraper.scrape_scores(forecast_date)

                if not games:
                    st.warning(f"No games scheduled for {forecast_date.strftime('%Y-%m-%d')}")
                else:
                    predictions_list = []
                    for game in games:
                        is_neutral = True if game[0] == 1 else False
                        winner, prob, home_spread = predictions.predict_game(
                            elo_state, game[3], game[1], pick_mode=1, neutral=is_neutral
                        )

                        if game[1] == winner:
                            predictions_list.append([
                                '✓' if game[0] == 1 else '',
                                game[1],
                                prob,
                                -home_spread,
                                game[3],
                                "{0:.0%}".format(1 - (float(prob[:-1])/100)),
                                home_spread
                            ])
                        else:
                            predictions_list.append([
                                '✓' if game[0] == 1 else '',
                                game[1],
                                "{0:.0%}".format(1 - (float(prob[:-1])/100)),
                                -home_spread,
                                game[3],
                                prob,
                                home_spread
                            ])

                    df = pd.DataFrame(
                        predictions_list,
                        columns=['Neutral', 'Away', 'Away Win Prob.', 'Away Pred. Spread',
                                'Home', 'Home Win Prob.', 'Home Pred. Spread']
                    )

                    # Mark new teams
                    df['Away'] = df['Away'].apply(
                        lambda x: x + "*" if elo_state.get_elo(x) == elo.NEW_ELO else x
                    )
                    df['Home'] = df['Home'].apply(
                        lambda x: x + "*" if elo_state.get_elo(x) == elo.NEW_ELO else x
                    )

                    st.success(f"Predictions for {forecast_date.strftime('%Y-%m-%d')} based on ratings through {elo_state.date}")
                    st.info("* indicates teams new to the system (predictions may be less reliable)")

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

            except Exception as e:
                st.error(f"Error generating predictions: {str(e)}")

elif page == "Single Game Predictor":
    st.header("⚔️ Single Game Predictor")

    st.markdown("""
    Predict the outcome of a hypothetical matchup between any two teams.
    This is useful for games not yet scheduled or what-if scenarios.
    """)

    col1, col2 = st.columns(2)

    # Get available teams
    with st.spinner("Loading team data..."):
        elo_state = get_elo_state()
        all_teams = sorted(list(elo_state.teams.keys()))

    with col1:
        home_team = st.selectbox(
            "Home Team",
            options=all_teams,
            index=all_teams.index("Duke") if "Duke" in all_teams else 0
        )

    with col2:
        away_team = st.selectbox(
            "Away Team",
            options=all_teams,
            index=all_teams.index("North Carolina") if "North Carolina" in all_teams else 1
        )

    neutral_site = st.checkbox("Neutral Site Game")

    use_historical = st.checkbox("Use historical ELO ratings")
    if use_historical:
        hist_date = st.date_input(
            "Calculate ratings as of this date",
            value=datetime.date.today() - datetime.timedelta(days=7),
            min_value=datetime.date(2010, 11, 1),
            max_value=datetime.date.today()
        )
        stop_short = hist_date.strftime('%Y%m%d')
        elo_state = get_elo_state(stop_short)

    if st.button("Predict Game", type="primary"):
        if home_team == away_team:
            st.error("Please select different teams!")
        else:
            winner, prob, home_spread = predictions.predict_game(
                elo_state, home_team, away_team, neutral=neutral_site, pick_mode=1
            )

            st.success(f"Ratings through {elo_state.date}")

            # Display matchup info
            if neutral_site:
                st.subheader(f"{home_team} vs. {away_team} @ Neutral Site")
            else:
                st.subheader(f"{away_team} @ {home_team}")

            # Get ELO ratings
            home_elo = elo_state.get_elo(home_team)
            away_elo = elo_state.get_elo(away_team)

            # Display prediction results
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    label=f"{home_team} ELO",
                    value=f"{home_elo:.0f}"
                )

            with col2:
                st.metric(
                    label="Predicted Spread",
                    value=f"{abs(home_spread):.1f}",
                    delta=f"{home_team if home_spread > 0 else away_team} favored"
                )

            with col3:
                st.metric(
                    label=f"{away_team} ELO",
                    value=f"{away_elo:.0f}"
                )

            # Win probabilities
            home_prob = float(prob[:-1])/100 if winner == home_team else 1 - float(prob[:-1])/100
            away_prob = 1 - home_prob

            st.markdown("---")
            st.subheader("Win Probabilities")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {home_team}")
                st.progress(home_prob)
                st.markdown(f"**{home_prob:.1%}**")

            with col2:
                st.markdown(f"### {away_team}")
                st.progress(away_prob)
                st.markdown(f"**{away_prob:.1%}**")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Data source: <a href='https://www.scoresandodds.com/ncaab'>Scores and Odds</a> |
    Methodology inspired by <a href='https://fivethirtyeight.com/'>FiveThirtyEight</a></p>
    <p><a href='https://github.com/grdavis/college-basketball-elo'>View on GitHub</a></p>
</div>
""", unsafe_allow_html=True)
