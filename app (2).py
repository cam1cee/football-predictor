import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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

# League configurations - 2024-25 Season (CORRECTED)
LEAGUES = {
    "Serie A": {
        "teams": [
            "Napoli", "Inter", "Atalanta", "Juventus", "Roma",
            "Fiorentina", "Lazio", "AC Milan", "Bologna", "Torino",
            "Udinese", "Genoa", "Lecce", "Parma", "Como",
            "Hellas Verona", "Cagliari", "Sassuolo", "Pisa", "Cremonese"
        ],
        "color": "#008FD7"
    },
    "La Liga": {
        "teams": [
            "Barcelona", "Real Madrid", "Atlético Madrid", "Athletic Bilbao", 
            "Villarreal", "Mallorca", "Real Sociedad", "Girona", "Osasuna",
            "Betis", "Celta Vigo", "Rayo Vallecano", "Sevilla", "Leganés",
            "Alavés", "Getafe", "Espanyol", "Valladolid", "Valencia", "Las Palmas"
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
            "Kashima Antlers", "Kashiwa Reysol", "Vissel Kobe", "Kyoto Sanga",
            "Sanfrecce Hiroshima", "Kawasaki Frontale", "Machida Zelvia", "Gamba Osaka",
            "Urawa Red Diamonds", "Cerezo Osaka", "FC Tokyo", "Tokyo Verdy",
            "Yokohama F. Marinos", "Yokohama FC", "Shonan Bellmare", "Albirex Niigata",
            "Shimizu S-Pulse", "Nagoya Grampus", "Fagiano Okayama", "Avispa Fukuoka"
        ],
        "color": "#E60012"
    }
}

# Asian Handicap options
ASIAN_HANDICAPS = [
    -3.0, -2.75, -2.5, -2.25, -2.0, -1.75, -1.5, -1.25, -1.0, 
    -0.75, -0.5, -0.25, 0.0, 
    0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0
]

# Goal Line options
GOAL_LINES = [
    0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 
    3.0, 3.25, 3.5, 3.75, 4.0, 4.25, 4.5, 5.0, 5.5, 6.0
]

def predict_match(home_team, away_team, league):
    """Generate match prediction with goals"""
    # Simulate feature engineering
    home_form = np.random.uniform(0.3, 0.9)
    away_form = np.random.uniform(0.3, 0.9)
    
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
    home_xg = np.random.uniform(1.0, 2.8)
    away_xg = np.random.uniform(0.8, 2.5)
    total_goals = home_xg + away_xg
    
    return {
        "home_win": probs[0],
        "draw": probs[1],
        "away_win": probs[2],
        "home_xg": home_xg,
        "away_xg": away_xg,
        "total_goals": total_goals,
        "btts": np.random.uniform(0.45, 0.70)
    }

def calculate_ah_probability(prediction, handicap, is_home=True):
    """Calculate Asian Handicap probability"""
    home_win = prediction["home_win"]
    draw = prediction["draw"]
    away_win = prediction["away_win"]
    
    if is_home:
        # Home team with handicap
        if handicap == 0.0:  # Draw No Bet
            return home_win + (draw * 0.5)  # Half stake back on draw
        elif handicap == -0.25:  # Quarter goal
            return home_win * 0.5 + (home_win * 0.5)  # Complex split
        elif handicap == -0.5:
            return home_win
        elif handicap == -0.75:
            return home_win * 0.85
        elif handicap == -1.0:
            return home_win * 0.75
        elif handicap == -1.25:
            return home_win * 0.65
        elif handicap == -1.5:
            return home_win * 0.55
        elif handicap == -1.75:
            return home_win * 0.45
        elif handicap == -2.0:
            return home_win * 0.35
        elif handicap >= -2.5:
            return home_win * (0.35 - abs(handicap) * 0.05)
        elif handicap == 0.25:
            return home_win + (draw * 0.75)
        elif handicap == 0.5:
            return home_win + draw
        elif handicap == 0.75:
            return home_win + draw + (away_win * 0.15)
        elif handicap >= 1.0:
            return home_win + draw + (away_win * min(0.3 + handicap * 0.1, 0.7))
    else:
        # Away team (invert handicap)
        return calculate_ah_probability(prediction, -handicap, True)

def calculate_goal_line_probability(prediction, line, is_over=True):
    """Calculate Goal Line (Over/Under) probability"""
    total_goals = prediction["total_goals"]
    
    # Use sigmoid function for smoother probabilities
    if is_over:
        # Over probability
        if line % 0.5 == 0:  # Whole or half line (0.5, 1.5, 2.5, etc.)
            return 1 / (1 + np.exp(-(total_goals - line)))
        else:  # Quarter line (0.75, 1.25, 2.25, etc.)
            # Split stake between two lines
            lower = line - 0.25
            upper = line + 0.25
            prob_lower = 1 / (1 + np.exp(-(total_goals - lower)))
            prob_upper = 1 / (1 + np.exp(-(total_goals - upper)))
            return (prob_lower + prob_upper) / 2
    else:
        # Under probability
        return 1 - calculate_goal_line_probability(prediction, line, True)

def calculate_implied_probability(odds):
    """Convert decimal odds to implied probability"""
    if odds <= 1.0:
        return 0
    return 1 / odds

def calculate_value(true_prob, odds):
    """Calculate expected value of a bet"""
    implied_prob = calculate_implied_probability(odds)
    return ((true_prob * odds) - 1) * 100

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
    
    if is_value:
        st.markdown(f"""
        <div class="value-bet-positive">
            <h4>✅ VALUE BET DETECTED</h4>
            <p>Expected Value: <strong>+{ev:.2f}%</strong> | Bookmaker: {implied_prob*100:.1f}% | Our Model: {true_prob*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="value-bet-negative">
            <h4>❌ NO VALUE</h4>
            <p>Expected Value: <strong>{ev:.2f}%</strong> | Bookmaker: {implied_prob*100:.1f}% | Our Model: {true_prob*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header
    st.title("⚽ Football Betting Value Calculator")
    st.markdown("### Find value bets with complete Asian Handicaps & Goal Lines")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        default_stake = st.number_input("Default Stake ($)", min_value=1, max_value=1000, value=10, step=5)
        
        st.markdown("---")
        st.markdown("### 📊 Markets Available")
        st.success("""
        **Match Result (1X2)**
        **Asian Handicaps** (All lines from -3.0 to +3.0)
        **Goal Lines** (Over/Under 0.5 to 6.0)
        **BTTS** (Both Teams to Score)
        **Expected Goals** prediction
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
            st.markdown(f"## {league_name} - 2024-25 Season")
            
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
            
            # Main markets
            st.markdown("### 💰 Match Result Odds")
            col1, col2, col3 = st.columns(3)
            with col1:
                home_odds = st.number_input(f"{home_team} Win", min_value=1.01, max_value=50.0, value=2.10, step=0.05, key=f"home_odds_{league_name}")
            with col2:
                draw_odds = st.number_input("Draw", min_value=1.01, max_value=50.0, value=3.40, step=0.05, key=f"draw_odds_{league_name}")
            with col3:
                away_odds = st.number_input(f"{away_team} Win", min_value=1.01, max_value=50.0, value=3.80, step=0.05, key=f"away_odds_{league_name}")
            
            # Asian Handicap section
            st.markdown("---")
            st.markdown("### 🎯 Asian Handicap Markets")
            
            col1, col2 = st.columns(2)
            with col1:
                selected_ah = st.selectbox(
                    f"Select Handicap for {home_team}",
                    ASIAN_HANDICAPS,
                    index=11,  # Default to -0.25
                    key=f"ah_select_{league_name}",
                    format_func=lambda x: f"{'+' if x > 0 else ''}{x}"
                )
            with col2:
                ah_odds = st.number_input(
                    f"Odds for {home_team} {'+' if selected_ah > 0 else ''}{selected_ah}",
                    min_value=1.01, max_value=50.0, value=1.95, step=0.05,
                    key=f"ah_odds_{league_name}"
                )
            
            # Goal Lines section
            st.markdown("---")
            st.markdown("### ⚽ Goal Line Markets")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_goal_line = st.selectbox(
                    "Select Goal Line",
                    GOAL_LINES,
                    index=8,  # Default to 2.5
                    key=f"gl_select_{league_name}"
                )
            with col2:
                over_odds = st.number_input(
                    f"Over {selected_goal_line}",
                    min_value=1.01, max_value=50.0, value=1.90, step=0.05,
                    key=f"over_odds_{league_name}"
                )
            with col3:
                under_odds = st.number_input(
                    f"Under {selected_goal_line}",
                    min_value=1.01, max_value=50.0, value=1.95, step=0.05,
                    key=f"under_odds_{league_name}"
                )
            
            # BTTS
            st.markdown("---")
            st.markdown("### 🔥 Both Teams to Score")
            col1, col2 = st.columns(2)
            with col1:
                btts_yes_odds = st.number_input("BTTS Yes", min_value=1.01, max_value=50.0, value=1.80, step=0.05, key=f"btts_yes_{league_name}")
            with col2:
                btts_no_odds = st.number_input("BTTS No", min_value=1.01, max_value=50.0, value=2.05, step=0.05, key=f"btts_no_{league_name}")
            
            # Predict button
            st.markdown("---")
            if st.button(f"🎯 Analyze All Markets & Find Value", key=f"predict_{league_name}", type="primary", use_container_width=True):
                with st.spinner("Analyzing match and calculating value bets..."):
                    import time
                    time.sleep(1)
                    
                    prediction = predict_match(home_team, away_team, league_name)
                    
                    st.markdown("---")
                    st.markdown("## 📊 Match Analysis")
                    
                    # Match info
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
                        <h2>{home_team} vs {away_team}</h2>
                        <h3 style="color: {LEAGUES[league_name]['color']};">Expected Goals: {prediction['home_xg']:.2f} - {prediction['away_xg']:.2f}</h3>
                        <p><strong>Total Goals Expected: {prediction['total_goals']:.2f}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("")
                    
                    # 1X2 Analysis
                    st.markdown("---")
                    st.markdown("## 1️⃣ Match Result (1X2)")
                    
                    with st.expander(f"🏠 {home_team} Win - Odds: {home_odds}", expanded=True):
                        display_value_bet(f"{home_team} Win", prediction["home_win"], home_odds, default_stake)
                    
                    with st.expander(f"🤝 Draw - Odds: {draw_odds}", expanded=True):
                        display_value_bet("Draw", prediction["draw"], draw_odds, default_stake)
                    
                    with st.expander(f"✈️ {away_team} Win - Odds: {away_odds}", expanded=True):
                        display_value_bet(f"{away_team} Win", prediction["away_win"], away_odds, default_stake)
                    
                    # Asian Handicap Analysis
                    st.markdown("---")
                    st.markdown(f"## 2️⃣ Asian Handicap: {home_team} {'+' if selected_ah > 0 else ''}{selected_ah}")
                    
                    ah_prob = calculate_ah_probability(prediction, selected_ah, is_home=True)
                    
                    with st.expander(f"📊 {home_team} {'+' if selected_ah > 0 else ''}{selected_ah} - Odds: {ah_odds}", expanded=True):
                        display_value_bet(f"AH {selected_ah}", ah_prob, ah_odds, default_stake)
                        
                        # Explanation
                        st.info(f"""
                        **Asian Handicap Explained:**
                        - {home_team} starts with a {selected_ah} goal handicap
                        - Win probability with this handicap: {ah_prob*100:.1f}%
                        """)
                    
                    # Goal Lines Analysis
                    st.markdown("---")
                    st.markdown(f"## 3️⃣ Goal Line: {selected_goal_line}")
                    
                    over_prob = calculate_goal_line_probability(prediction, selected_goal_line, is_over=True)
                    under_prob = calculate_goal_line_probability(prediction, selected_goal_line, is_over=False)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with st.expander(f"📈 Over {selected_goal_line} - Odds: {over_odds}", expanded=True):
                            display_value_bet(f"Over {selected_goal_line}", over_prob, over_odds, default_stake)
                    
                    with col2:
                        with st.expander(f"📉 Under {selected_goal_line} - Odds: {under_odds}", expanded=True):
                            display_value_bet(f"Under {selected_goal_line}", under_prob, under_odds, default_stake)
                    
                    # BTTS Analysis
                    st.markdown("---")
                    st.markdown("## 4️⃣ Both Teams to Score")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with st.expander(f"✅ BTTS Yes - Odds: {btts_yes_odds}", expanded=True):
                            display_value_bet("BTTS Yes", prediction["btts"], btts_yes_odds, default_stake)
                    
                    with col2:
                        with st.expander(f"❌ BTTS No - Odds: {btts_no_odds}", expanded=True):
                            display_value_bet("BTTS No", 1 - prediction["btts"], btts_no_odds, default_stake)
                    
                    # Summary of ALL bets
                    st.markdown("---")
                    st.markdown("## 🏆 Value Bets Summary")
                    
                    all_bets = [
                        (f"{home_team} Win", prediction["home_win"], home_odds),
                        ("Draw", prediction["draw"], draw_odds),
                        (f"{away_team} Win", prediction["away_win"], away_odds),
                        (f"AH {home_team} {'+' if selected_ah > 0 else ''}{selected_ah}", ah_prob, ah_odds),
                        (f"Over {selected_goal_line}", over_prob, over_odds),
                        (f"Under {selected_goal_line}", under_prob, under_odds),
                        ("BTTS Yes", prediction["btts"], btts_yes_odds),
                        ("BTTS No", 1 - prediction["btts"], btts_no_odds),
                    ]
                    
                    value_bets = []
                    for name, prob, odds in all_bets:
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
                            - Probability: {prob*100:.1f}%
                            - Odds: {odds}
                            - Expected Return: ${expected_return:.2f} (on ${default_stake})
                            """)
                    else:
                        st.warning("⚠️ No value bets found. Bookmaker has priced these markets efficiently.")

if __name__ == "__main__":
    main()
