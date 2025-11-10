"""
Team Rankings Page
View top ELO-rated teams with current ratings and trends
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import elo
from datetime import datetime, timedelta

st.set_page_config(page_title="Team Rankings", page_icon="📊", layout="wide")

st.title("📊 Team Rankings")
st.markdown("View the top ELO-rated college basketball teams")

# Sidebar controls
st.sidebar.header("Settings")
num_teams = st.sidebar.slider("Number of teams to display", 10, 100, 50)
period_days = st.sidebar.slider("Rating change period (days)", 1, 30, 7)

# Date selector
st.sidebar.subheader("Historical Rankings")
use_historical = st.sidebar.checkbox("View rankings as of a past date")

if use_historical:
    selected_date = st.sidebar.date_input(
        "Select date",
        value=datetime.now().date(),
        min_value=datetime(2010, 11, 1).date(),
        max_value=datetime.now().date()
    )
    stop_date = selected_date.strftime('%Y%m%d')
else:
    stop_date = '99999999'  # Latest
    selected_date = datetime.now().date()

# Load ELO data
with st.spinner("Loading ELO ratings..."):
    try:
        # Force refresh if using latest data
        elo_state = elo.main(stop_short=stop_date)
        top_teams = elo_state.get_top(num_teams)

        if not top_teams or len(top_teams) == 0:
            st.error("No teams found. Please check that game data is available.")
            st.stop()

        # Display date
        st.info(f"📅 Rankings as of: **{elo_state.date}**")

        # Create DataFrame
        df = pd.DataFrame(top_teams, columns=['Team', 'ELO Rating', f'{period_days}-Day Change'])

        # Add rank column
        df.insert(0, 'Rank', range(1, len(df) + 1))

        # Calculate point spread vs next rank
        spreads = []
        for i in range(len(df) - 1):
            elo_diff = df.iloc[i]['ELO Rating'] - df.iloc[i + 1]['ELO Rating']
            spread = elo_diff / elo.ELO_TO_POINTS_FACTOR
            spreads.append(round(spread, 1))
        spreads.append(None)  # Last team has no next opponent
        df['Spread vs Next'] = spreads

        # Format columns
        df['ELO Rating'] = df['ELO Rating'].round(0).astype(int)

        # Convert day change from string ('+3') to int
        try:
            df[f'{period_days}-Day Change'] = pd.to_numeric(
                df[f'{period_days}-Day Change'].astype(str).str.replace('+', ''),
                errors='coerce'
            ).fillna(0).astype(int)
        except Exception as e:
            st.warning(f"Could not format day change column: {e}")
            # Keep as is if conversion fails

        # Display table
        st.subheader(f"Top {num_teams} Teams")

        # Create Plotly table
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(df.columns),
                fill_color='#1f77b4',
                align='left',
                font=dict(color='white', size=14)
            ),
            cells=dict(
                values=[df[col] for col in df.columns],
                fill_color=[['#f0f2f6' if i % 2 == 0 else 'white' for i in range(len(df))]],
                align='left',
                font=dict(size=12),
                height=30
            )
        )])

        fig.update_layout(
            height=min(800, len(df) * 35 + 100),
            margin=dict(l=0, r=0, t=0, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Display as regular dataframe as well for easy searching
        with st.expander("🔍 Searchable Table"):
            st.dataframe(df, use_container_width=True, hide_index=True)

        # Top 10 visualization
        if len(df) >= 10:
            st.subheader("Top 10 Teams - ELO Ratings")

            top_10 = df.head(10).copy()

            fig_bar = go.Figure(data=[
                go.Bar(
                    x=top_10['ELO Rating'],
                    y=top_10['Team'],
                    orientation='h',
                    marker=dict(
                        color=top_10['ELO Rating'],
                        colorscale='Blues',
                        showscale=True
                    ),
                    text=top_10['ELO Rating'],
                    textposition='outside'
                )
            ])

            fig_bar.update_layout(
                xaxis_title="ELO Rating",
                yaxis_title="",
                height=400,
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(fig_bar, use_container_width=True)

        # Download data
        st.download_button(
            label="📥 Download Rankings (CSV)",
            data=df.to_csv(index=False),
            file_name=f"team_rankings_{elo_state.date}.csv",
            mime="text/csv"
        )

        # Explanations
        with st.expander("ℹ️ Understanding the Rankings"):
            st.markdown("""
            ### What is ELO?

            **ELO ratings** account for strength of schedule. A team with fewer wins
            but tougher opponents may be rated higher than an undefeated team with
            an easy schedule.

            ### Column Explanations

            - **Rank**: Current position in the rankings
            - **Team**: Team name
            - **ELO Rating**: Current ELO rating (higher is better)
                - Typical range: 1000-2200
                - Average team: ~1500
                - Elite teams: 2000+
            - **{}-Day Change**: How much the rating has changed in the last {} days
                - Positive = improving
                - Negative = declining
            - **Spread vs Next**: Predicted point spread against the next-ranked team
                - Example: A value of 2.5 means this team would be favored by 2.5 points

            ### How Ratings Work

            - Ratings increase with wins, decrease with losses
            - Beating higher-rated opponents earns more points
            - Losing to lower-rated opponents costs more points
            - Home court advantage: +82 ELO (~3.3 points)
            """.format(period_days, period_days))

    except Exception as e:
        st.error(f"Error loading rankings: {e}")
        st.info("Make sure the ELO system has been initialized with game data.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Data updates daily at 9 AM EST via GitHub Actions</p>
</div>
""", unsafe_allow_html=True)
