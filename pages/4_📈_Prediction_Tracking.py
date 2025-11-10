"""
Prediction Tracking Page
Real-time monitoring of prediction accuracy and model performance
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import prediction_tracker
import os

# Title
st.title("📈 Prediction Tracking & Performance")
st.markdown("Monitor prediction accuracy over time with interactive analytics")

# Sidebar
st.sidebar.header("Filters & Settings")

# Load data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_predictions_data():
    """Load predictions database"""
    try:
        db = prediction_tracker.load_database()
        # Convert date columns to datetime
        db['game_date'] = pd.to_datetime(db['game_date'], format='%Y%m%d')
        db['prediction_date'] = pd.to_datetime(db['prediction_date'], format='%Y%m%d')
        return db
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return pd.DataFrame()

db = load_predictions_data()

if db.empty:
    st.warning("No prediction data available yet. Predictions will appear here once the system starts tracking games.")
    st.info("📝 The tracking system will automatically populate this dashboard as predictions are made and results come in.")
    st.stop()

# Filter to only played games
played_games = db[db['game_played'] == 1].copy()

if played_games.empty:
    st.warning("No completed games with predictions yet. Check back after some games have been played!")
    st.info(f"📊 Total predictions stored: {len(db)}")
    st.stop()

# Date range filter
st.sidebar.subheader("Date Range")
min_date = played_games['game_date'].min()
max_date = played_games['game_date'].max()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date.date(),
    max_value=max_date.date()
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_games = played_games[
        (played_games['game_date'] >= pd.Timestamp(start_date)) &
        (played_games['game_date'] <= pd.Timestamp(end_date))
    ].copy()
else:
    filtered_games = played_games.copy()

# Additional filters
st.sidebar.subheader("Additional Filters")
neutral_filter = st.sidebar.multiselect(
    "Game Type",
    options=['Home/Away', 'Neutral'],
    default=['Home/Away', 'Neutral']
)

# Apply neutral filter
neutral_values = []
if 'Home/Away' in neutral_filter:
    neutral_values.append(0)
if 'Neutral' in neutral_filter:
    neutral_values.append(1)
filtered_games = filtered_games[filtered_games['neutral'].isin(neutral_values)]

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Data Range:** {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
st.sidebar.markdown(f"**Total Games:** {len(played_games)}")
st.sidebar.markdown(f"**Filtered Games:** {len(filtered_games)}")

# Main dashboard
if len(filtered_games) > 0:
    # Calculate metrics
    total_games = len(filtered_games)
    correct = filtered_games['prediction_correct'].sum()
    accuracy = correct / total_games if total_games > 0 else 0

    # Brier score
    brier = ((filtered_games['predicted_home_win_prob'] - filtered_games['home_won']) ** 2).mean()

    # Spread error
    mean_spread_error = filtered_games['spread_error'].mean()
    median_spread_error = filtered_games['spread_error'].median()

    # Vegas comparison
    vegas_games = filtered_games[filtered_games['vegas_spread'].notna()]
    if len(vegas_games) > 0:
        vegas_games['vegas_error'] = abs(vegas_games['actual_spread'] - vegas_games['vegas_spread'])
        beat_vegas = (vegas_games['spread_error'] < vegas_games['vegas_error']).sum() / len(vegas_games)
    else:
        beat_vegas = None

    # Overview metrics
    st.header("📊 Overview Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Win/Loss Accuracy",
            f"{accuracy:.1%}",
            delta=f"{correct}/{total_games}"
        )

    with col2:
        st.metric(
            "Brier Score",
            f"{brier:.4f}",
            delta="Lower is better",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            "Mean Spread Error",
            f"{mean_spread_error:.2f} pts",
            delta=f"Median: {median_spread_error:.2f}"
        )

    with col4:
        if beat_vegas is not None:
            st.metric(
                "Beat Vegas",
                f"{beat_vegas:.1%}",
                delta=f"{len(vegas_games)} games"
            )
        else:
            st.metric("Beat Vegas", "N/A", delta="No data")

    with col5:
        recent_7_days = filtered_games[filtered_games['game_date'] >= (max_date - timedelta(days=7))]
        if len(recent_7_days) > 0:
            recent_acc = recent_7_days['prediction_correct'].sum() / len(recent_7_days)
            st.metric(
                "Last 7 Days",
                f"{recent_acc:.1%}",
                delta=f"{len(recent_7_days)} games"
            )
        else:
            st.metric("Last 7 Days", "N/A", delta="No data")

    # Accuracy over time
    st.header("📈 Accuracy Trends Over Time")

    col1, col2 = st.columns(2)

    with col1:
        # Rolling accuracy
        filtered_games_sorted = filtered_games.sort_values('game_date')
        window = st.slider("Rolling window (games)", 5, 50, 20)

        filtered_games_sorted['rolling_accuracy'] = filtered_games_sorted['prediction_correct'].rolling(window=window, min_periods=1).mean()

        fig_acc = px.line(
            filtered_games_sorted,
            x='game_date',
            y='rolling_accuracy',
            title=f'Rolling Accuracy ({window}-game window)',
            labels={'rolling_accuracy': 'Accuracy', 'game_date': 'Date'}
        )
        fig_acc.add_hline(y=0.5, line_dash="dash", line_color="gray", annotation_text="50% baseline")
        fig_acc.update_yaxes(tickformat='.0%', range=[0.3, 1.0])
        st.plotly_chart(fig_acc, use_container_width=True)

    with col2:
        # Brier score over time
        filtered_games_sorted['brier'] = (filtered_games_sorted['predicted_home_win_prob'] - filtered_games_sorted['home_won']) ** 2
        filtered_games_sorted['rolling_brier'] = filtered_games_sorted['brier'].rolling(window=window, min_periods=1).mean()

        fig_brier = px.line(
            filtered_games_sorted,
            x='game_date',
            y='rolling_brier',
            title=f'Rolling Brier Score ({window}-game window)',
            labels={'rolling_brier': 'Brier Score', 'game_date': 'Date'}
        )
        fig_brier.add_hline(y=0.25, line_dash="dash", line_color="gray", annotation_text="Random guessing")
        fig_brier.update_yaxes(range=[0, 0.3])
        st.plotly_chart(fig_brier, use_container_width=True)

    # Spread performance
    st.header("📏 Spread Performance")

    col1, col2 = st.columns(2)

    with col1:
        # Spread error distribution
        fig_spread_dist = px.histogram(
            filtered_games,
            x='spread_error',
            nbins=30,
            title='Spread Error Distribution',
            labels={'spread_error': 'Spread Error (points)', 'count': 'Number of Games'}
        )
        fig_spread_dist.add_vline(x=mean_spread_error, line_dash="dash", line_color="red", annotation_text=f"Mean: {mean_spread_error:.2f}")
        st.plotly_chart(fig_spread_dist, use_container_width=True)

    with col2:
        # Spread error over time
        filtered_games_sorted['rolling_spread_error'] = filtered_games_sorted['spread_error'].rolling(window=window, min_periods=1).mean()

        fig_spread_time = px.line(
            filtered_games_sorted,
            x='game_date',
            y='rolling_spread_error',
            title=f'Rolling Spread Error ({window}-game window)',
            labels={'rolling_spread_error': 'Mean Spread Error (pts)', 'game_date': 'Date'}
        )
        st.plotly_chart(fig_spread_time, use_container_width=True)

    # Calibration analysis
    st.header("🎯 Probability Calibration")

    col1, col2 = st.columns(2)

    with col1:
        # Calibration curve
        bins = np.arange(0.5, 1.01, 0.05)
        bin_labels = [f"{int(b*100)}-{int((b+0.05)*100)}%" for b in bins[:-1]]

        calibration_data = []
        for i in range(len(bins)-1):
            lower, upper = bins[i], bins[i+1]

            # Home team predictions in this bin
            home_mask = (filtered_games['predicted_home_win_prob'] >= lower) & (filtered_games['predicted_home_win_prob'] < upper)
            home_games = filtered_games[home_mask]

            # Away team predictions in this bin
            away_mask = (filtered_games['predicted_home_win_prob'] <= (1-lower)) & (filtered_games['predicted_home_win_prob'] > (1-upper))
            away_games = filtered_games[away_mask]

            bin_games = pd.concat([home_games, away_games])

            if len(bin_games) > 0:
                actual_win_rate = bin_games['prediction_correct'].mean()
                predicted_prob = (lower + upper) / 2
                calibration_data.append({
                    'predicted': predicted_prob,
                    'actual': actual_win_rate,
                    'games': len(bin_games),
                    'label': bin_labels[i]
                })

        calib_df = pd.DataFrame(calibration_data)

        fig_calib = go.Figure()
        fig_calib.add_trace(go.Scatter(
            x=calib_df['predicted'],
            y=calib_df['actual'],
            mode='markers+lines',
            name='Model Calibration',
            marker=dict(size=calib_df['games']*0.5, sizemode='diameter'),
            text=calib_df['label'],
            hovertemplate='<b>%{text}</b><br>Predicted: %{x:.1%}<br>Actual: %{y:.1%}<br>Games: %{marker.size:.0f}<extra></extra>'
        ))
        fig_calib.add_trace(go.Scatter(
            x=[0.5, 1.0],
            y=[0.5, 1.0],
            mode='lines',
            name='Perfect Calibration',
            line=dict(dash='dash', color='gray')
        ))
        fig_calib.update_layout(
            title='Calibration Curve (size = # of games)',
            xaxis_title='Predicted Win Probability',
            yaxis_title='Actual Win Rate',
            xaxis=dict(tickformat='.0%', range=[0.45, 1.05]),
            yaxis=dict(tickformat='.0%', range=[0.45, 1.05])
        )
        st.plotly_chart(fig_calib, use_container_width=True)

    with col2:
        # Confidence vs accuracy
        confidence_bins = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        conf_data = []

        for i in range(len(confidence_bins)-1):
            lower = confidence_bins[i]
            upper = confidence_bins[i+1]

            home_conf = filtered_games[
                (filtered_games['predicted_home_win_prob'] > lower) &
                (filtered_games['predicted_home_win_prob'] <= upper)
            ]

            away_conf = filtered_games[
                (filtered_games['predicted_home_win_prob'] < (1-lower)) &
                (filtered_games['predicted_home_win_prob'] >= (1-upper))
            ]

            conf_games = pd.concat([home_conf, away_conf])

            if len(conf_games) > 0:
                conf_data.append({
                    'confidence': f"{int(lower*100)}-{int(upper*100)}%",
                    'accuracy': conf_games['prediction_correct'].mean(),
                    'games': len(conf_games)
                })

        conf_df = pd.DataFrame(conf_data)

        fig_conf = go.Figure()
        fig_conf.add_trace(go.Bar(
            x=conf_df['confidence'],
            y=conf_df['accuracy'],
            text=[f"{a:.1%}<br>({g} games)" for a, g in zip(conf_df['accuracy'], conf_df['games'])],
            textposition='auto',
            marker_color='lightblue'
        ))
        fig_conf.update_layout(
            title='Accuracy by Confidence Level',
            xaxis_title='Predicted Confidence',
            yaxis_title='Actual Accuracy',
            yaxis=dict(tickformat='.0%', range=[0, 1])
        )
        st.plotly_chart(fig_conf, use_container_width=True)

    # Vegas comparison
    if len(vegas_games) > 0:
        st.header("💰 Performance vs Vegas Spreads")

        col1, col2 = st.columns(2)

        with col1:
            # ELO vs Vegas accuracy
            comparison_data = pd.DataFrame({
                'Model': ['ELO Model', 'Vegas Spreads'],
                'Mean Error': [vegas_games['spread_error'].mean(), vegas_games['vegas_error'].mean()],
                'Median Error': [vegas_games['spread_error'].median(), vegas_games['vegas_error'].median()]
            })

            fig_vegas = go.Figure()
            fig_vegas.add_trace(go.Bar(
                name='Mean Error',
                x=comparison_data['Model'],
                y=comparison_data['Mean Error'],
                text=[f"{v:.2f}" for v in comparison_data['Mean Error']],
                textposition='auto'
            ))
            fig_vegas.add_trace(go.Bar(
                name='Median Error',
                x=comparison_data['Model'],
                y=comparison_data['Median Error'],
                text=[f"{v:.2f}" for v in comparison_data['Median Error']],
                textposition='auto'
            ))
            fig_vegas.update_layout(
                title='Spread Error: ELO vs Vegas',
                yaxis_title='Spread Error (points)',
                barmode='group'
            )
            st.plotly_chart(fig_vegas, use_container_width=True)

        with col2:
            # Games where ELO beat Vegas
            vegas_games['beat_vegas'] = vegas_games['spread_error'] < vegas_games['vegas_error']
            beat_vegas_over_time = vegas_games.sort_values('game_date')
            beat_vegas_over_time['rolling_beat_vegas'] = beat_vegas_over_time['beat_vegas'].rolling(window=window, min_periods=1).mean()

            fig_beat_vegas = px.line(
                beat_vegas_over_time,
                x='game_date',
                y='rolling_beat_vegas',
                title=f'Rate of Beating Vegas ({window}-game window)',
                labels={'rolling_beat_vegas': 'Beat Vegas Rate', 'game_date': 'Date'}
            )
            fig_beat_vegas.add_hline(y=0.5, line_dash="dash", line_color="gray", annotation_text="50% baseline")
            fig_beat_vegas.update_yaxes(tickformat='.0%')
            st.plotly_chart(fig_beat_vegas, use_container_width=True)

    # Recent predictions
    st.header("🔍 Recent Predictions")

    num_recent = st.slider("Number of recent games to show", 10, 100, 25)

    recent_games = filtered_games.sort_values('game_date', ascending=False).head(num_recent).copy()

    # Format for display
    recent_games['result'] = recent_games.apply(
        lambda row: f"{row['away_team']} {int(row['actual_away_score'])} @ {row['home_team']} {int(row['actual_home_score'])}",
        axis=1
    )
    recent_games['predicted_winner'] = recent_games.apply(
        lambda row: row['home_team'] if row['predicted_home_win_prob'] > 0.5 else row['away_team'],
        axis=1
    )
    recent_games['confidence'] = recent_games['predicted_home_win_prob'].apply(
        lambda x: max(x, 1-x)
    )
    recent_games['correct'] = recent_games['prediction_correct'].map({1: '✅', 0: '❌'})

    display_df = recent_games[[
        'game_date', 'result', 'predicted_winner', 'confidence',
        'predicted_home_spread', 'spread_error', 'correct'
    ]].copy()

    display_df.columns = ['Date', 'Result', 'Predicted Winner', 'Confidence',
                          'Predicted Spread', 'Spread Error', 'Correct']
    display_df['Confidence'] = display_df['Confidence'].map(lambda x: f"{x:.1%}")
    display_df['Predicted Spread'] = display_df['Predicted Spread'].map(lambda x: f"{x:+.1f}")
    display_df['Spread Error'] = display_df['Spread Error'].map(lambda x: f"{x:.1f}")
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Download data
    st.header("💾 Export Data")

    col1, col2 = st.columns(2)

    with col1:
        csv = filtered_games.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"predictions_{start_date}_{end_date}.csv",
            mime="text/csv"
        )

    with col2:
        # Calculate summary metrics
        summary = {
            'Total Games': total_games,
            'Accuracy': f"{accuracy:.2%}",
            'Brier Score': f"{brier:.4f}",
            'Mean Spread Error': f"{mean_spread_error:.2f}",
            'Median Spread Error': f"{median_spread_error:.2f}",
        }
        if beat_vegas is not None:
            summary['Beat Vegas Rate'] = f"{beat_vegas:.2%}"

        st.json(summary)

else:
    st.warning("No games match the current filters. Try adjusting your date range or filters.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>College Basketball ELO Prediction Tracker | Data updates daily at 9 AM EST</p>
    <p>Built with Streamlit 🎈 | Last updated: {}</p>
</div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)
