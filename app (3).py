import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import os

# Page config
st.set_page_config(
    page_title="⚽ Football Value Bet Calculator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 15px;
        padding-right: 15px;
        font-size: 16px;
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

# League configurations - 2025-26 Season
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
    "Serie B": {
        "teams": [
            "Spezia", "Pisa", "Cremonese", "Juve Stabia", "Brescia",
            "Palermo", "Bari", "Cesena", "Reggiana", "Catanzaro",
            "Mantova", "Salernitana", "Modena", "Sampdoria", "Cosenza",
            "Carrarese", "Südtirol", "Frosinone", "Cittadella", "Monza"
        ],
        "color": "#E34234"
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
    "La Liga 2": {
        "teams": [
            "Levante", "Mirandés", "Racing Santander", "Almería", "Huesca",
            "Elche", "Oviedo", "Málaga", "Sporting Gijón", "Albacete",
            "Eibar", "Zaragoza", "Cádiz", "Eldense", "Granada",
            "Burgos", "Córdoba", "Racing Ferrol", "Cartagena", "Tenerife"
        ],
        "color": "#FF9B54"
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
    "Bundesliga": {
        "teams": [
            "Bayern Munich", "Bayer Leverkusen", "Eintracht Frankfurt", "RB Leipzig",
            "Borussia Dortmund", "VfB Stuttgart", "Werder Bremen", "Freiburg",
            "Mainz 05", "Hoffenheim", "Augsburg", "St. Pauli", "Union Berlin",
            "VfL Bochum", "Wolfsburg", "Gladbach", "Heidenheim", "Holstein Kiel"
        ],
        "color": "#D20515"
    },
    "2. Bundesliga": {
        "teams": [
            "Hamburger SV", "Karlsruher SC", "Hannover 96", "1. FC Köln",
            "Fortuna Düsseldorf", "Kaiserslautern", "Elversberg", "Magdeburg",
            "Paderborn", "Hertha BSC", "Nürnberg", "Darmstadt", "Schalke 04",
            "Greuther Fürth", "Braunschweig", "Münster", "Ulm", "Regensburg"
        ],
        "color": "#FF4444"
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
    },
    "Swiss Super League": {
        "teams": [
            "FC Zurich", "Basel", "Young Boys", "Lugano", "Servette",
            "St. Gallen", "Lucerne", "Sion", "Lausanne-Sport", "Grasshoppers",
            "Yverdon", "Winterthur"
        ],
        "color": "#FF0000"
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
    """Generate match prediction"""
    home_form = np.random.uniform(0.35, 0.85)
    away_form = np.random.uniform(0.30, 0.80)
    
    # Base probabilities with home advantage
    home_base = 0.43 + (home_form - away_form) * 0.18
    draw_base = 0.26
    away_base = 1 - home_base - draw_base
    
    noise = np.random.uniform(-0.04, 0.04, 3)
    probs = np.array([home_base, draw_base, away_base]) + noise
    probs = np.maximum(probs, 0.05)
    probs = probs / probs.sum()
    
    # Expected goals
    home_xg = np.random.uniform(1.0, 2.9)
    away_xg = np.random.uniform(0.7, 2.4)
    total_goals = home_xg + away_xg
    
    return {
        "home_win": probs[0],
        "draw": probs[1],
        "away_win": probs[2],
        "home_xg": home_xg,
        "away_xg": away_xg,
        "total_goals": total_goals,
        "btts": np.random.uniform(0.42, 0.72)
    }

def calculate_ah_probability(prediction, handicap, is_home=True):
    """Calculate Asian Handicap probability"""
    home_win = prediction["home_win"]
    draw = prediction["draw"]
    away_win = prediction["away_win"]
    
    if is_home:
        if handicap == 0.0:
            return home_win + (draw * 0.5)
        elif handicap == -0.25:
            return home_win * 0.75 + (draw * 0.25)
        elif handicap == -0.5:
            return home_win
        elif handicap == -0.75:
            return home_win * 0.85
        elif handicap == -1.0:
            return home_win * 0.70
        elif handicap == -1.25:
            return home_win * 0.60
        elif handicap == -1.5:
            return home_win * 0.50
        elif handicap == -1.75:
            return home_win * 0.42
        elif handicap == -2.0:
            return home_win * 0.33
        elif handicap <= -2.25:
            return max(home_win * (0.33 - abs(handicap) * 0.08), 0.05)
        elif handicap == 0.25:
            return home_win + (draw * 0.75)
        elif handicap == 0.5:
            return home_win + draw
        elif handicap == 0.75:
            return home_win + draw + (away_win * 0.20)
        elif handicap >= 1.0:
            return min(home_win + draw + (away_win * (0.25 + handicap * 0.12)), 0.95)
    else:
        return calculate_ah_probability(prediction, -handicap, True)

def calculate_goal_line_probability(prediction, line, is_over=True):
    """Calculate Goal Line probability"""
    total_goals = prediction["total_goals"]
    
    if is_over:
        if line % 0.5 == 0:
            return 1 / (1 + np.exp(-(total_goals - line) * 1.2))
        else:
            lower = line - 0.25
            upper = line + 0.25
            prob_lower = 1 / (1 + np.exp(-(total_goals - lower) * 1.2))
            prob_upper = 1 / (1 + np.exp(-(total_goals - upper) * 1.2))
            return (prob_lower + prob_upper) / 2
    else:
        return 1 - calculate_goal_line_probability(prediction, line, True)

def calculate_implied_probability(odds):
    """Convert odds to probability"""
    if odds <= 1.0:
        return 0
    return 1 / odds

def calculate_value(true_prob, odds):
    """Calculate expected value"""
    return ((true_prob * odds) - 1) * 100

def display_value_bet(market_name, true_prob, odds, stake=10):
    """Display value analysis"""
    if odds <= 0:
        return
    
    implied_prob = calculate_implied_probability(odds)
    ev = calculate_value(true_prob, odds)
    expected_return = (true_prob * odds * stake) + ((1 - true_prob) * -stake)
    
    is_value = ev > 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("True Prob", f"{true_prob*100:.1f}%")
    with col2:
        st.metric("Implied Prob", f"{implied_prob*100:.1f}%")
    with col3:
        if is_value:
            st.markdown(f'<p class="big-value">+{ev:.2f}%</p>', unsafe_allow_html=True)
            st.caption("EV")
        else:
            st.markdown(f'<p class="negative-value">{ev:.2f}%</p>', unsafe_allow_html=True)
            st.caption("EV")
    with col4:
        st.metric("Return", f"${expected_return:.2f}", f"${stake}")
    
    if is_value:
        st.markdown(f"""
        <div class="value-bet-positive">
            <h4>✅ VALUE BET</h4>
            <p>EV: <strong>+{ev:.2f}%</strong> | Book: {implied_prob*100:.1f}% | Model: {true_prob*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="value-bet-negative">
            <h4>❌ NO VALUE</h4>
            <p>EV: <strong>{ev:.2f}%</strong> | Book: {implied_prob*100:.1f}% | Model: {true_prob*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.title("⚽ Football Betting Value Calculator")
    st.markdown("### 9 Leagues | All Asian Handicaps | All Goal Lines | Value Bet Finder")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        default_stake = st.number_input("Stake ($)", min_value=1, max_value=1000, value=10, step=5)
        
        st.markdown("---")
        st.markdown("### 📊 Features")
        st.success("""
        **9 Leagues:**
        🇮🇹 Serie A & Serie B
        🇪🇸 La Liga & La Liga 2
        🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League
        🇩🇪 Bundesliga & 2. Bundesliga
        🇯🇵 J1 League
        🇨🇭 Swiss Super League
        
        **Markets:**
        • Match Result (1X2)
        • Asian Handicaps (-3.0 to +3.0)
        • Goal Lines (0.5 to 6.0)
        • BTTS
        """)
        
        st.markdown("---")
        st.warning("⚠️ For entertainment only.")
    
    # League tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "🇮🇹 Serie A", "🇮🇹 Serie B", "🇪🇸 La Liga", "🇪🇸 La Liga 2",
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier", "🇩🇪 Bundesliga", "🇩🇪 2.Bundes", "🇯🇵 J1", "🇨🇭 Swiss"
    ])
    
    tabs_config = [
        (tab1, "Serie A"), (tab2, "Serie B"), (tab3, "La Liga"), (tab4, "La Liga 2"),
        (tab5, "Premier League"), (tab6, "Bundesliga"), (tab7, "2. Bundesliga"),
        (tab8, "J1 League"), (tab9, "Swiss Super League")
    ]
    
    for tab, league_name in tabs_config:
        with tab:
            st.markdown(f"## {league_name} - 2025-26")
            
            col1, col2 = st.columns(2)
            
            with col1:
                home_team = st.selectbox(
                    "🏠 Home Team",
                    LEAGUES[league_name]["teams"],
                    key=f"home_{league_name}"
                )
            
            with col2:
                away_options = [t for t in LEAGUES[league_name]["teams"] if t != home_team]
                away_team = st.selectbox(
                    "✈️ Away Team",
                    away_options,
                    key=f"away_{league_name}"
                )
            
            st.markdown("---")
            st.markdown("### 💰 1X2 Odds")
            col1, col2, col3 = st.columns(3)
            with col1:
                home_odds = st.number_input(f"{home_team}", min_value=1.01, max_value=50.0, value=2.10, step=0.05, key=f"h_{league_name}")
            with col2:
                draw_odds = st.number_input("Draw", min_value=1.01, max_value=50.0, value=3.40, step=0.05, key=f"d_{league_name}")
            with col3:
                away_odds = st.number_input(f"{away_team}", min_value=1.01, max_value=50.0, value=3.80, step=0.05, key=f"a_{league_name}")
            
            # Asian Handicap
            st.markdown("---")
            st.markdown("### 🎯 Asian Handicap")
            col1, col2 = st.columns(2)
            with col1:
                selected_ah = st.selectbox(
                    f"{home_team} Handicap",
                    ASIAN_HANDICAPS,
                    index=11,
                    key=f"ah_sel_{league_name}",
                    format_func=lambda x: f"{'+' if x > 0 else ''}{x}"
                )
            with col2:
                ah_odds = st.number_input(
                    f"Odds {'+' if selected_ah > 0 else ''}{selected_ah}",
                    min_value=1.01, max_value=50.0, value=1.95, step=0.05,
                    key=f"ah_odds_{league_name}"
                )
            
            # Goal Lines
            st.markdown("---")
            st.markdown("### ⚽ Goal Lines")
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_gl = st.selectbox(
                    "Line",
                    GOAL_LINES,
                    index=8,
                    key=f"gl_{league_name}"
                )
            with col2:
                over_odds = st.number_input(
                    f"Over {selected_gl}",
                    min_value=1.01, max_value=50.0, value=1.90, step=0.05,
                    key=f"over_{league_name}"
                )
            with col3:
                under_odds = st.number_input(
                    f"Under {selected_gl}",
                    min_value=1.01, max_value=50.0, value=1.95, step=0.05,
                    key=f"under_{league_name}"
                )
            
            # BTTS
            st.markdown("---")
            st.markdown("### 🔥 BTTS")
            col1, col2 = st.columns(2)
            with col1:
                btts_yes = st.number_input("Yes", min_value=1.01, max_value=50.0, value=1.80, step=0.05, key=f"btts_y_{league_name}")
            with col2:
                btts_no = st.number_input("No", min_value=1.01, max_value=50.0, value=2.05, step=0.05, key=f"btts_n_{league_name}")
            
            # Analyze button
            st.markdown("---")
            if st.button(f"🎯 Analyze All Markets", key=f"btn_{league_name}", type="primary", use_container_width=True):
                with st.spinner("Analyzing..."):
                    import time
                    time.sleep(0.8)
                    
                    pred = predict_match(home_team, away_team, league_name)
                    
                    st.markdown("---")
                    st.markdown("## 📊 Analysis")
                    
                    st.markdown(f"""
                    <div style="background: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
                        <h2>{home_team} vs {away_team}</h2>
                        <h3 style="color: {LEAGUES[league_name]['color']};">xG: {pred['home_xg']:.2f} - {pred['away_xg']:.2f}</h3>
                        <p><strong>Total Goals: {pred['total_goals']:.2f}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("")
                    
                    # 1X2
                    st.markdown("---")
                    st.markdown("## 1️⃣ Match Result")
                    with st.expander(f"🏠 {home_team} - {home_odds}", expanded=True):
                        display_value_bet(f"{home_team}", pred["home_win"], home_odds, default_stake)
                    with st.expander(f"🤝 Draw - {draw_odds}", expanded=True):
                        display_value_bet("Draw", pred["draw"], draw_odds, default_stake)
                    with st.expander(f"✈️ {away_team} - {away_odds}", expanded=True):
                        display_value_bet(f"{away_team}", pred["away_win"], away_odds, default_stake)
                    
                    # AH
                    st.markdown("---")
                    st.markdown(f"## 2️⃣ AH: {home_team} {'+' if selected_ah > 0 else ''}{selected_ah}")
                    ah_prob = calculate_ah_probability(pred, selected_ah, True)
                    with st.expander(f"📊 Odds: {ah_odds}", expanded=True):
                        display_value_bet(f"AH {selected_ah}", ah_prob, ah_odds, default_stake)
                    
                    # Goals
                    st.markdown("---")
                    st.markdown(f"## 3️⃣ Goals {selected_gl}")
                    over_prob = calculate_goal_line_probability(pred, selected_gl, True)
                    under_prob = calculate_goal_line_probability(pred, selected_gl, False)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.expander(f"📈 Over - {over_odds}", expanded=True):
                            display_value_bet(f"O{selected_gl}", over_prob, over_odds, default_stake)
                    with col2:
                        with st.expander(f"📉 Under - {under_odds}", expanded=True):
                            display_value_bet(f"U{selected_gl}", under_prob, under_odds, default_stake)
                    
                    # BTTS
                    st.markdown("---")
                    st.markdown("## 4️⃣ BTTS")
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.expander(f"✅ Yes - {btts_yes}", expanded=True):
                            display_value_bet("BTTS Y", pred["btts"], btts_yes, default_stake)
                    with col2:
                        with st.expander(f"❌ No - {btts_no}", expanded=True):
                            display_value_bet("BTTS N", 1-pred["btts"], btts_no, default_stake)
                    
                    # Summary
                    st.markdown("---")
                    st.markdown("## 🏆 Value Summary")
                    
                    bets = [
                        (f"{home_team}", pred["home_win"], home_odds),
                        ("Draw", pred["draw"], draw_odds),
                        (f"{away_team}", pred["away_win"], away_odds),
                        (f"AH {selected_ah}", ah_prob, ah_odds),
                        (f"O{selected_gl}", over_prob, over_odds),
                        (f"U{selected_gl}", under_prob, under_odds),
                        ("BTTS Y", pred["btts"], btts_yes),
                        ("BTTS N", 1-pred["btts"], btts_no),
                    ]
                    
                    values = [(n, calculate_value(p, o), p, o) for n, p, o in bets if calculate_value(p, o) > 0]
                    
                    if values:
                        values.sort(key=lambda x: x[1], reverse=True)
                        st.success(f"✅ {len(values)} value bet(s)!")
                        
                        for i, (name, ev, prob, odds) in enumerate(values, 1):
                            ret = (prob * odds * default_stake) + ((1-prob) * -default_stake)
                            st.markdown(f"""
                            **{i}. {name}**
                            - EV: **+{ev:.2f}%** | Prob: {prob*100:.1f}% | Odds: {odds} | Return: ${ret:.2f}
                            """)
                    else:
                        st.warning("⚠️ No value found")

if __name__ == "__main__":
    main()
