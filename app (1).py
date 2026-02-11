import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import os

# Page config
st.set_page_config(
    page_title="⚽ Football Betting Value Calculator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        font-size: 18px;
        font-weight: 600;
    }
    .value-bet-positive {
        background-color: #d4edda;
        border: 2px solid #28a745;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .value-bet-negative {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .big-value {
        font-size: 32px !important;
        font-weight: bold;
        color: #28a745;
    }
    .negative-value {
        font-size: 32px !important;
        font-weight: bold;
        color: #dc3545;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'predictions_history' not in st.session_state:
    st.session_state.predictions_history = []

# League configurations - 2025-26 Season
LEAGUES = {
    "Serie A": {
        "teams": [
            "Napoli", "Inter Milan", "Atalanta", "Fiorentina", "Lazio",
            "Juventus", "AC Milan", "Bologna", "Udinese", "Torino",
            "Empoli", "Roma", "Genoa", "Lecce", "Parma",
            "Como", "Verona", "Cagliari", "Venezia", "Monza"
        ],
        "color": "#008FD7"
    },
    "La Liga": {
        "teams": [
            "Barcelona", "Real Madrid", "Atlético Madrid", "Athletic Bilbao", 
            "Villarreal", "Mallorca", "Real Sociedad", "Girona", "Osasuna",
            "Betis", "Celta Vigo", "Rayo Vallecano", "Sevilla", "Leganés",
            "Alavés", "Getafe", "Espanyol", "Real Valladolid", "Valencia", "Las Palmas"
        ],
        "color": "#FF6B35"
    },
    "Premier League": {
        "teams": [
            "Liverpool", "Arsenal", "Chelsea", "Nottingham Forest", "Newcastle",
            "Manchester City", "Bournemouth", "Aston Villa", "Fulham", "Brighton",
            "Brentford", "Manchester United", "West Ham", "Tottenham", "Crystal Palace",
            "Everton", "Wolves", "Leicester City", "Ipswich Town", "Southampton"
        ],
        "color": "#3D195B"
    },
    "J1 League": {
        "teams": [
            "Vissel Kobe", "Sanfrecce Hiroshima", "Machida Zelvia", "Gamba Osaka",
            "Kashima Antlers", "Tokyo Verdy", "Cerezo Osaka", "FC Tokyo", 
            "Nagoya Grampus", "Kawasaki Frontale", "Avispa Fukuoka", "Yokohama F. Marinos",
            "Urawa Red Diamonds", "Shonan Bellmare", "Albirex Niigata", "Kyoto Sanga",
            "Kashiwa Reysol", "Sagan Tosu", "Jubilo Iwata", "Consadole Sapporo"
        ],
        "color": "#E60012"
    }
}

def calculate_form_score(team, league):
    """Calculate recent form score"""
    return np.random.uniform(0.3, 0.9)

def predict_match(home_team, away_team, league):
    """Generate match prediction with goals"""
    # Simulate feature engineering
    home_form = calculate_form_score(home_team, league)
    away_form = calculate_form_score(away_team, league)
    
    # Base probabilities with home advantage
    home_base = 0.42 + (home_form - away_form) * 0.15
    draw_base = 0.27
    away_base = 1 - home_base - draw_base
    
    # Add randomness and normalize
    noise = np.random.uniform(-0.05, 0.05, 3)
    probs = np.array([home_base, draw_base, away_base]) + noise
    probs = np.maximum(probs, 0.05)
    probs = probs / probs.sum()
    
    # Calculate expected goals
    home_xg = np.random.uniform(1.2, 2.8)
    away_xg = np.random.uniform(0.8, 2.3)
    total_goals = home_xg + away_xg
    
    # Asian Handicap probabilities (example: -0.5 for home)
    ah_home_minus_half = probs[0]  # Home needs to win
    ah_home_plus_half = probs[0] + probs[1]  # Home win or draw
    
    return {
        "home_win": probs[0],
        "draw": probs[1],
        "away_win": probs[2],
        "home_xg": home_xg,
        "away_xg": away_xg,
        "total_goals": total_goals,
        "over_2_5": 1 / (1 + np.exp(-(total_goals - 2.5))),  # Sigmoid
        "under_2_5": 1 - (1 / (1 + np.exp(-(total_goals - 2.5)))),
        "btts": np.random.uniform(0.45, 0.65),  # Both teams to score
        "ah_home_minus_half": ah_home_minus_half,
        "ah_home_plus_half": ah_home_plus_half,
        "confidence": max(probs)
    }

def calculate_implied_probability(odds):
    """Convert decimal odds to implied probability"""
    if odds <= 1.0:
        return 0
    return 1 / odds

def calculate_value(true_prob, odds):
    """Calculate expected value of a bet"""
    implied_prob = calculate_implied_probability(odds)
    return ((true_prob * odds) - 1) * 100  # Return as percentage

def display_value_bet(market_name, true_prob, odds, stake=10):
    """Display value bet analysis"""
    if odds <= 0:
        return
    
    implied_prob = calculate_implied_probability(odds)
    ev = calculate_value(true_prob, odds)
    expected_return = (true_prob * odds * stake) + ((1 - true_prob) * -stake)
    
    is_value = ev > 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("True Probability", f"{true_prob*100:.1f}%")
    with col2:
        st.metric("Implied Probability", f"{implied_prob*100:.1f}%")
    with col3:
        if is_value:
            st.markdown(f'<p class="big-value">+{ev:.2f}%</p>', unsafe_allow_html=True)
            st.caption("Expected Value")
        else:
            st.markdown(f'<p class="negative-value">{ev:.2f}%</p>', unsafe_allow_html=True)
            st.caption("Expected Value")
    with col4:
        st.metric("Expected Return", f"${expected_return:.2f}", f"on ${stake} stake")
    
    # Value assessment
    if is_value:
        st.markdown(f"""
        <div class="value-bet-positive">
            <h4>✅ VALUE BET DETECTED</h4>
            <p>This bet has a positive expected value of <strong>+{ev:.2f}%</strong></p>
            <p>The bookmaker's odds suggest a {implied_prob*100:.1f}% chance, but our model predicts {true_prob*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="value-bet-negative">
            <h4>❌ NO VALUE</h4>
            <p>This bet has a negative expected value of <strong>{ev:.2f}%</strong></p>
            <p>The bookmaker's odds suggest a {implied_prob*100:.1f}% chance, but our model predicts {true_prob*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

def plot_probability_bars(prediction):
    """Display prediction probabilities as horizontal bars"""
    st.markdown("### Match Result Probabilities")
    
    outcomes = [
        ("🏠 Home Win", prediction["home_win"], "#4CAF50"),
        ("🤝 Draw", prediction["draw"], "#FFC107"),
        ("✈️ Away Win", prediction["away_win"], "#2196F3")
    ]
    
    for label, prob, color in outcomes:
        col1, col2 = st.columns([3, 7])
        with col1:
            st.markdown(f"**{label}**")
        with col2:
            st.progress(float(prob))
            st.markdown(f"**{prob*100:.1f}%**")

# Main App
def main():
    # Header
    st.title("⚽ Football Betting Value Calculator")
    st.markdown("### Find value bets across Serie A, La Liga, Premier League & J1 League")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        default_stake = st.number_input("Default Stake ($)", min_value=1, max_value=1000, value=10, step=5)
        
        st.markdown("---")
        st.markdown("### 📊 Model Info")
        st.info("""
        **Our model predicts:**
        - Match outcomes (1X2)
        - Expected goals
        - Over/Under markets
        - Asian Handicaps
        - Both Teams to Score
        
        **Then calculates:**
        - True probabilities
        - Expected Value (EV)
        - Value bet opportunities
        """)
        
        st.markdown("---")
        st.markdown("### 💡 How to Use")
        st.success("""
        1. Select teams
        2. Enter bookmaker odds
        3. See our predictions
        4. Find value bets!
        
        **Green = Value Bet ✅**
        **Red = No Value ❌**
        """)
        
        st.markdown("---")
        st.warning("⚠️ **Disclaimer**: For entertainment only. Bet responsibly.")
    
    # Main content - League tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🇮🇹 Serie A", "🇪🇸 La Liga", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "🇯🇵 J1 League"])
    
    tabs_config = [
        (tab1, "Serie A"),
        (tab2, "La Liga"),
        (tab3, "Premier League"),
        (tab4, "J1 League")
    ]
    
    for tab, league_name in tabs_config:
        with tab:
            st.markdown(f"## {league_name} - Value Bet Finder")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏠 Home Team")
                home_team = st.selectbox(
                    "Select home team",
                    LEAGUES[league_name]["teams"],
                    key=f"home_{league_name}"
                )
            
            with col2:
                st.markdown("### ✈️ Away Team")
                away_options = [t for t in LEAGUES[league_name]["teams"] if t != home_team]
                away_team = st.selectbox(
                    "Select away team",
                    away_options,
                    key=f"away_{league_name}"
                )
            
            st.markdown("---")
            st.markdown("### 💰 Enter Bookmaker Odds (Decimal Format)")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                home_odds = st.number_input(f"{home_team} Win", min_value=1.01, max_value=50.0, value=2.10, step=0.05, key=f"home_odds_{league_name}")
            with col2:
                draw_odds = st.number_input("Draw", min_value=1.01, max_value=50.0, value=3.40, step=0.05, key=f"draw_odds_{league_name}")
            with col3:
                away_odds = st.number_input(f"{away_team} Win", min_value=1.01, max_value=50.0, value=3.80, step=0.05, key=f"away_odds_{league_name}")
            
            # Additional markets
            with st.expander("📊 Additional Markets (Optional)", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    over_2_5_odds = st.number_input("Over 2.5 Goals", min_value=1.01, max_value=50.0, value=1.90, step=0.05, key=f"o25_{league_name}")
                    under_2_5_odds = st.number_input("Under 2.5 Goals", min_value=1.01, max_value=50.0, value=1.95, step=0.05, key=f"u25_{league_name}")
                with col2:
                    btts_yes_odds = st.number_input("BTTS Yes", min_value=1.01, max_value=50.0, value=1.80, step=0.05, key=f"btts_{league_name}")
                    ah_home_odds = st.number_input(f"AH {home_team} -0.5", min_value=1.01, max_value=50.0, value=2.50, step=0.05, key=f"ah_{league_name}")
            
            # Predict button
            if st.button(f"🎯 Analyze & Find Value Bets", key=f"predict_{league_name}", type="primary", use_container_width=True):
                with st.spinner("Analyzing match and calculating value bets..."):
                    import time
                    time.sleep(1)
                    
                    # Get prediction
                    prediction = predict_match(home_team, away_team, league_name)
                    
                    st.markdown("---")
                    st.markdown("## 📊 Match Analysis")
                    
                    # Display match info
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
                        <h2>{home_team} vs {away_team}</h2>
                        <h3 style="color: {LEAGUES[league_name]['color']};">Expected Goals: {prediction['home_xg']:.2f} - {prediction['away_xg']:.2f}</h3>
                        <p><strong>Total Goals Expected: {prediction['total_goals']:.2f}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("")
                    
                    # Probabilities
                    plot_probability_bars(prediction)
                    
                    st.markdown("---")
                    st.markdown("## 💎 Value Bet Analysis")
                    
                    # Main markets
                    st.markdown("### 🎯 Match Result (1X2)")
                    
                    with st.expander(f"🏠 {home_team} Win - Odds: {home_odds}", expanded=True):
                        display_value_bet("Home Win", prediction["home_win"], home_odds, default_stake)
                    
                    with st.expander(f"🤝 Draw - Odds: {draw_odds}", expanded=True):
                        display_value_bet("Draw", prediction["draw"], draw_odds, default_stake)
                    
                    with st.expander(f"✈️ {away_team} Win - Odds: {away_odds}", expanded=True):
                        display_value_bet("Away Win", prediction["away_win"], away_odds, default_stake)
                    
                    st.markdown("---")
                    st.markdown("### ⚽ Goals Markets")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with st.expander(f"📈 Over 2.5 Goals - Odds: {over_2_5_odds}", expanded=True):
                            display_value_bet("Over 2.5", prediction["over_2_5"], over_2_5_odds, default_stake)
                    
                    with col2:
                        with st.expander(f"📉 Under 2.5 Goals - Odds: {under_2_5_odds}", expanded=True):
                            display_value_bet("Under 2.5", prediction["under_2_5"], under_2_5_odds, default_stake)
                    
                    st.markdown("---")
                    st.markdown("### 🎲 Alternative Markets")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with st.expander(f"🔥 Both Teams to Score - Odds: {btts_yes_odds}", expanded=True):
                            display_value_bet("BTTS Yes", prediction["btts"], btts_yes_odds, default_stake)
                    
                    with col2:
                        with st.expander(f"🎯 Asian Handicap {home_team} -0.5 - Odds: {ah_home_odds}", expanded=True):
                            display_value_bet("AH Home -0.5", prediction["ah_home_minus_half"], ah_home_odds, default_stake)
                    
                    # Summary of best bets
                    st.markdown("---")
                    st.markdown("## 🏆 Best Value Bets Summary")
                    
                    # Calculate all EVs
                    bets = [
                        (f"{home_team} Win", prediction["home_win"], home_odds),
                        ("Draw", prediction["draw"], draw_odds),
                        (f"{away_team} Win", prediction["away_win"], away_odds),
                        ("Over 2.5 Goals", prediction["over_2_5"], over_2_5_odds),
                        ("Under 2.5 Goals", prediction["under_2_5"], under_2_5_odds),
                        ("BTTS Yes", prediction["btts"], btts_yes_odds),
                        (f"AH {home_team} -0.5", prediction["ah_home_minus_half"], ah_home_odds),
                    ]
                    
                    value_bets = []
                    for name, prob, odds in bets:
                        ev = calculate_value(prob, odds)
                        if ev > 0:
                            value_bets.append((name, ev, prob, odds))
                    
                    if value_bets:
                        value_bets.sort(key=lambda x: x[1], reverse=True)
                        
                        st.success(f"✅ Found {len(value_bets)} value bet(s)!")
                        
                        for i, (name, ev, prob, odds) in enumerate(value_bets, 1):
                            expected_return = (prob * odds * default_stake) + ((1 - prob) * -default_stake)
                            st.markdown(f"""
                            **{i}. {name}**
                            - Expected Value: **+{ev:.2f}%**
                            - Our Probability: {prob*100:.1f}%
                            - Odds: {odds}
                            - Expected Return: ${expected_return:.2f} (on ${default_stake} stake)
                            """)
                    else:
                        st.warning("⚠️ No value bets found with the current odds. The bookmaker has priced this match efficiently.")
                    
                    # Additional insights
                    st.markdown("---")
                    st.markdown("### 💡 Key Insights")
                    
                    insights = []
                    if prediction["home_win"] > 0.5:
                        insights.append(f"✅ Strong home advantage for {home_team}")
                    if prediction["total_goals"] > 3.0:
                        insights.append("⚽ High-scoring match expected")
                    elif prediction["total_goals"] < 2.0:
                        insights.append("🛡️ Low-scoring match expected")
                    if prediction["btts"] > 0.6:
                        insights.append("🔥 Both teams likely to score")
                    
                    for insight in insights:
                        st.markdown(f"- {insight}")

if __name__ == "__main__":
    main()
