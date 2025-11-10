"""
Game Predictions Page
View predictions for upcoming games
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import elo
import predictions as pred
import scraper
from datetime import datetime, timedelta

st.set_page_config(page_title="Game Predictions", page_icon="🎯", layout="wide")

st.title("🎯 Game Predictions")
st.markdown("Predictions for scheduled college basketball games")

# Sidebar controls
st.sidebar.header("Settings")

# Date selector
forecast_date = st.sidebar.date_input(
    "Select game date",
    value=datetime.now().date(),
    min_value=datetime(2024, 11, 1).date(),
    max_value=(datetime.now() + timedelta(days=30)).date()
)

# Historical cutoff (for testing past predictions)
use_historical = st.sidebar.checkbox("Make predictions as of a past date")
if use_historical:
    cutoff_date = st.sidebar.date_input(
        "Use ratings through",
        value=forecast_date - timedelta(days=1),
        max_value=forecast_date
    )
    stop_short = cutoff_date.strftime('%Y%m%d')
else:
    stop_short = '99999999'
    cutoff_date = None

# Load predictions
st.info(f"📅 Predictions for games on: **{forecast_date.strftime('%Y-%m-%d')}**")

if use_historical:
    st.info(f"📊 Using ELO ratings through: **{cutoff_date.strftime('%Y-%m-%d')}**")

try:
    with st.spinner("Loading predictions..."):
        # Load ELO state
        elo_state = elo.main(stop_short=stop_short)

        # Get scheduled games
        scraper.scrape_neutral_data()
        games = scraper.scrape_scores(forecast_date)

        if not games or len(games) == 0:
            st.warning(f"No games scheduled for {forecast_date.strftime('%Y-%m-%d')}")
            st.info("Try selecting a different date, or check back later as schedules are updated.")
        else:
            # Generate predictions
            predictions = []
            for game in games:
                is_neutral = True if game[0] == 1 else False
                winner, prob, home_spread = pred.predict_game(
                    elo_state,
                    game[3],  # home
                    game[1],  # away
                    pick_mode=1,
                    neutral=is_neutral
                )

                # Format prediction
                if game[1] == winner:
                    # Away team favored
                    predictions.append([
                        game[0],  # neutral
                        game[1],  # away team
                        prob,  # away win prob
                        -home_spread,  # away pred spread
                        game[3],  # home team
                        f"{(1 - float(prob[:-1])/100):.0%}",  # home win prob
                        home_spread  # home pred spread
                    ])
                else:
                    # Home team favored
                    predictions.append([
                        game[0],
                        game[1],
                        f"{(1 - float(prob[:-1])/100):.0%}",
                        -home_spread,
                        game[3],
                        prob,
                        home_spread
                    ])

            # Create DataFrame
            df = pd.DataFrame(predictions, columns=[
                'Neutral', 'Away', 'Away Win Prob.', 'Away Pred. Spread',
                'Home', 'Home Win Prob.', 'Home Pred. Spread'
            ])

            # Add favorite indicator
            df['Favorite'] = df.apply(
                lambda row: row['Home'] if float(row['Home Win Prob.'].strip('%')) > 50 else row['Away'],
                axis=1
            )

            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Games", len(df))

            with col2:
                neutral_games = df[df['Neutral'] == 1]
                st.metric("Neutral Site Games", len(neutral_games))

            with col3:
                # Average predicted margin
                df['margin'] = df['Home Pred. Spread'].abs()
                avg_margin = df['margin'].mean()
                st.metric("Avg. Predicted Margin", f"{avg_margin:.1f} pts")

            with col4:
                # Close games (< 5 point spread)
                close_games = df[df['margin'] < 5]
                st.metric("Close Games (< 5 pts)", len(close_games))

            # Display predictions table
            st.subheader(f"{len(df)} Games Predicted")

            # Create Plotly table
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=['Neutral', 'Away', 'Away Win %', 'Away Spread', 'Home', 'Home Win %', 'Home Spread', 'Favorite'],
                    fill_color='#1f77b4',
                    align='left',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=[df[col] for col in df.columns],
                    fill_color=[['#f0f2f6' if i % 2 == 0 else 'white' for i in range(len(df))]],
                    align='left',
                    font=dict(size=11),
                    height=28
                )
            )])

            fig.update_layout(
                height=min(700, len(df) * 32 + 80),
                margin=dict(l=0, r=0, t=0, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)

            # Searchable table
            with st.expander("🔍 Searchable Table"):
                st.dataframe(df, use_container_width=True, hide_index=True)

            # Visualizations
            st.subheader("Prediction Distribution")

            col1, col2 = st.columns(2)

            with col1:
                # Win probability distribution
                home_probs = [float(p.strip('%')) / 100 for p in df['Home Win Prob.']]
                away_probs = [float(p.strip('%')) / 100 for p in df['Away Win Prob.']]
                all_probs = [max(h, a) for h, a in zip(home_probs, away_probs)]

                fig_hist = go.Figure(data=[go.Histogram(
                    x=all_probs,
                    nbinsx=20,
                    marker_color='lightblue'
                )])
                fig_hist.update_layout(
                    title="Win Probability Distribution (Favorite)",
                    xaxis_title="Win Probability",
                    yaxis_title="Number of Games",
                    xaxis=dict(tickformat='.0%')
                )
                st.plotly_chart(fig_hist, use_container_width=True)

            with col2:
                # Spread distribution
                all_spreads = df['Home Pred. Spread'].abs()

                fig_spread = go.Figure(data=[go.Histogram(
                    x=all_spreads,
                    nbinsx=20,
                    marker_color='lightgreen'
                )])
                fig_spread.update_layout(
                    title="Predicted Spread Distribution",
                    xaxis_title="Point Spread (Favorite)",
                    yaxis_title="Number of Games"
                )
                st.plotly_chart(fig_spread, use_container_width=True)

            # Download data
            st.download_button(
                label="📥 Download Predictions (CSV)",
                data=df.to_csv(index=False),
                file_name=f"predictions_{forecast_date.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

            # Explanations
            with st.expander("ℹ️ Understanding the Predictions"):
                st.markdown("""
                ### How Predictions Work

                **Win Probability** is calculated from ELO difference:
                ```
                P(win) = 1 / (1 + 10^(-elo_difference/400))
                ```

                **Point Spread** is derived from ELO:
                ```
                Spread = elo_difference / -24.78
                ```

                ### Column Explanations

                - **Neutral**: 1 = neutral site, 0 = home/away
                - **Win Probability**: Chance each team wins (0-100%)
                - **Predicted Spread**: Point spread (negative = favored)
                    - Example: -5.5 means favored by 5.5 points
                - **Favorite**: Team predicted to win

                ### Home Court Advantage

                - Home teams get +82 ELO boost (~3.3 points)
                - No advantage at neutral sites

                ### Interpreting Results

                - **High Confidence**: Win prob > 80%
                - **Moderate Confidence**: Win prob 60-80%
                - **Toss-up**: Win prob 50-60%
                - **Close Games**: Spread < 5 points
                """)

except Exception as e:
    st.error(f"Error generating predictions: {e}")
    import traceback
    st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Predictions update daily | Vegas spreads added when available</p>
</div>
""", unsafe_allow_html=True)
