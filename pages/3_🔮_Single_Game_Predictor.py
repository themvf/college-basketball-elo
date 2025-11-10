"""
Single Game Predictor Page
Predict outcomes of custom matchups between any two teams
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import elo
import predictions as pred
from datetime import datetime

st.set_page_config(page_title="Single Game Predictor", page_icon="🔮", layout="wide")

st.title("🔮 Single Game Predictor")
st.markdown("Predict the outcome of any matchup between two teams")

# Sidebar controls
st.sidebar.header("Settings")

# Historical date selector
use_historical = st.sidebar.checkbox("Use ratings from a past date")
if use_historical:
    selected_date = st.sidebar.date_input(
        "Ratings as of",
        value=datetime.now().date(),
        min_value=datetime(2010, 11, 1).date(),
        max_value=datetime.now().date()
    )
    stop_short = selected_date.strftime('%Y%m%d')
else:
    stop_short = '99999999'
    selected_date = None

# Load ELO state
try:
    with st.spinner("Loading ELO ratings..."):
        elo_state = elo.main(stop_short=stop_short)

        # Get all team names
        all_teams = sorted([team.name for team in elo_state.team_list])

        if use_historical:
            st.info(f"📊 Using ELO ratings as of: **{elo_state.date}**")
        else:
            st.info(f"📊 Using latest ELO ratings through: **{elo_state.date}**")

        # Team selection
        st.subheader("Select Teams")

        col1, col2, col3 = st.columns([2, 1, 2])

        with col1:
            home_team = st.selectbox(
                "Home Team",
                options=all_teams,
                index=all_teams.index("Duke") if "Duke" in all_teams else 0,
                key="home"
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>vs.</h3>", unsafe_allow_html=True)

        with col3:
            away_team = st.selectbox(
                "Away Team",
                options=all_teams,
                index=all_teams.index("UNC") if "UNC" in all_teams else 1,
                key="away"
            )

        # Game location
        neutral = st.checkbox("Neutral Site Game", value=False)

        if home_team == away_team:
            st.warning("⚠️ Please select two different teams")
        else:
            # Get predictions
            winner, prob, home_spread = pred.predict_game(
                elo_state,
                home_team,
                away_team,
                pick_mode=1,
                neutral=neutral
            )

            # Get ELO ratings
            home_elo = elo_state.get_elo(home_team)
            away_elo = elo_state.get_elo(away_team)

            # Apply home advantage for display
            if not neutral:
                home_advantage = pred.add_home_advantage(home_elo)
                home_elo_adj = home_elo + home_advantage
            else:
                home_advantage = 0
                home_elo_adj = home_elo

            # Calculate probabilities
            elo_diff = home_elo_adj - away_elo
            home_win_prob = 1 / (1 + 10**(-elo_diff/400))
            away_win_prob = 1 - home_win_prob

            # Display prediction
            st.markdown("---")
            st.subheader("Prediction Results")

            # Large metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"### {home_team}")
                st.metric("Base ELO", f"{home_elo:.0f}")
                if not neutral:
                    st.metric("Home Advantage", f"+{home_advantage:.0f}")
                    st.metric("Adjusted ELO", f"{home_elo_adj:.0f}")
                st.metric("Win Probability", f"{home_win_prob:.1%}", delta=None)

            with col2:
                st.markdown("### Prediction")
                st.markdown(f"<h1 style='text-align: center; color: {'green' if winner == home_team else 'red'};'>{winner}</h1>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align: center;'>Wins</h3>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center;'>{prob}</h2>", unsafe_allow_html=True)

                if home_spread > 0:
                    st.markdown(f"<p style='text-align: center; font-size: 20px;'>{away_team} by {abs(home_spread):.1f}</p>", unsafe_allow_html=True)
                elif home_spread < 0:
                    st.markdown(f"<p style='text-align: center; font-size: 20px;'>{home_team} by {abs(home_spread):.1f}</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='text-align: center; font-size: 20px;'>Even</p>", unsafe_allow_html=True)

            with col3:
                st.markdown(f"### {away_team}")
                st.metric("Base ELO", f"{away_elo:.0f}")
                if not neutral:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                st.metric("Win Probability", f"{away_win_prob:.1%}", delta=None)

            # Visualization
            st.markdown("---")
            st.subheader("Win Probability Visualization")

            # Create probability bar chart
            fig = go.Figure()

            fig.add_trace(go.Bar(
                y=[home_team],
                x=[home_win_prob * 100],
                orientation='h',
                name=home_team,
                marker=dict(color='lightblue'),
                text=[f"{home_win_prob:.1%}"],
                textposition='inside',
                textfont=dict(size=16)
            ))

            fig.add_trace(go.Bar(
                y=[away_team],
                x=[away_win_prob * 100],
                orientation='h',
                name=away_team,
                marker=dict(color='lightcoral'),
                text=[f"{away_win_prob:.1%}"],
                textposition='inside',
                textfont=dict(size=16)
            ))

            fig.update_layout(
                xaxis=dict(
                    title="Win Probability (%)",
                    range=[0, 100],
                    ticksuffix="%"
                ),
                yaxis=dict(title=""),
                height=250,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

            # Detailed breakdown
            with st.expander("📊 Detailed Breakdown"):
                breakdown_data = {
                    "Metric": [
                        "Base ELO Rating",
                        "Home Court Advantage" if not neutral else "Neutral Site",
                        "Adjusted ELO",
                        "ELO Difference",
                        "Win Probability",
                        "Predicted Spread"
                    ],
                    home_team: [
                        f"{home_elo:.0f}",
                        f"+{home_advantage:.0f}" if not neutral else "N/A",
                        f"{home_elo_adj:.0f}",
                        f"+{elo_diff:.0f}" if elo_diff > 0 else f"{elo_diff:.0f}",
                        f"{home_win_prob:.2%}",
                        f"{home_spread:+.1f}"
                    ],
                    away_team: [
                        f"{away_elo:.0f}",
                        "0" if not neutral else "N/A",
                        f"{away_elo:.0f}",
                        f"{-elo_diff:.0f}" if elo_diff < 0 else f"{-elo_diff:.0f}",
                        f"{away_win_prob:.2%}",
                        f"{-home_spread:+.1f}"
                    ]
                }

                breakdown_df = pd.DataFrame(breakdown_data)
                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

            # Key insights
            st.markdown("---")
            st.subheader("Key Insights")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Matchup Assessment:**")

                if abs(elo_diff) < 50:
                    st.info("🔥 This is a **toss-up** game! Very evenly matched.")
                elif abs(elo_diff) < 100:
                    st.info(f"⚖️ This is a **competitive** matchup with a slight edge to {winner}.")
                elif abs(elo_diff) < 200:
                    st.info(f"👍 {winner} is a **solid favorite** in this matchup.")
                else:
                    st.info(f"💪 {winner} is a **heavy favorite** and should win comfortably.")

            with col2:
                st.markdown("**Spread Context:**")

                abs_spread = abs(home_spread)
                if abs_spread < 3:
                    st.info("📊 **Pick'em** - Essentially a toss-up.")
                elif abs_spread < 7:
                    st.info("📊 **Close game** - Expected to be competitive.")
                elif abs_spread < 12:
                    st.info("📊 **Moderate favorite** - Clear advantage but not a blowout.")
                else:
                    st.info("📊 **Heavy favorite** - Large expected margin of victory.")

            # Similar matchups (optional enhancement)
            st.markdown("---")
            with st.expander("🔍 How This Works"):
                st.markdown(f"""
                ### Prediction Methodology

                **1. ELO Ratings**
                - {home_team}: {home_elo:.0f}
                - {away_team}: {away_elo:.0f}

                **2. Home Court Advantage**
                {"- " + home_team + " gets +" + f"{home_advantage:.0f}" + " ELO boost for playing at home" if not neutral else "- No advantage at neutral site"}

                **3. Win Probability Calculation**
                ```
                P(home win) = 1 / (1 + 10^(-elo_diff/400))
                P(home win) = 1 / (1 + 10^(-{elo_diff:.0f}/400))
                P(home win) = {home_win_prob:.4f} = {home_win_prob:.1%}
                ```

                **4. Point Spread Conversion**
                ```
                Spread = elo_difference / -24.78
                Spread = {elo_diff:.0f} / -24.78
                Spread = {home_spread:.1f}
                ```

                ### Understanding ELO
                - **Average team**: ~1500 ELO
                - **Good team**: 1700-1900 ELO
                - **Elite team**: 2000+ ELO
                - **100 ELO difference** ≈ 64% win probability, 4 point spread
                """)

except Exception as e:
    st.error(f"Error loading predictor: {e}")
    import traceback
    st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Make custom predictions for any matchup | Test hypothetical scenarios</p>
</div>
""", unsafe_allow_html=True)
