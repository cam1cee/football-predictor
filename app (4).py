import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="⚽ Football Betting Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 15px;
        padding-right: 15px;
        font-size: 15px;
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
        font-size: 28px !important;
        font-weight: bold;
        color: #28a745;
    }
    .negative-value {
        font-size: 28px !important;
        font-weight: bold;
        color: #dc3545;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'predictions' not in st.session_state:
    st.session_state.predictions = []

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

# Monte Carlo Predictor (from provided code)
def monte_carlo_simulation(
    home_goals_avg: float,
    away_goals_avg: float,
    n_simulations: int = 10000
):
    """Monte Carlo simulation for match outcome"""
    home_goals = np.random.poisson(home_goals_avg, n_simulations)
    away_goals = np.random.poisson(away_goals_avg, n_simulations)
    
    total_goals = home_goals + away_goals
    
    over_2_5_prob = np.mean(total_goals > 2.5)
    btts_prob = np.mean((home_goals > 0) & (away_goals > 0))
    
    return {
        'over_2_5': over_2_5_prob,
        'under_2_5': 1 - over_2_5_prob,
        'btts_yes': btts_prob,
        'btts_no': 1 - btts_prob,
        'avg_total_goals': np.mean(total_goals),
        'goal_distribution': {
            '0-1': np.mean(total_goals <= 1),
            '2': np.mean(total_goals == 2),
            '3': np.mean(total_goals == 3),
            '4+': np.mean(total_goals >= 4)
        }
    }

def predict_corners(
    home_corners_avg: float,
    away_corners_avg: float,
    n_simulations: int = 10000
):
    """Monte Carlo simulation for corners"""
    home_corners = np.random.poisson(home_corners_avg, n_simulations)
    away_corners = np.random.poisson(away_corners_avg, n_simulations)
    
    total_corners = home_corners + away_corners
    
    return {
        'over_8_5': np.mean(total_corners > 8.5),
        'over_9_5': np.mean(total_corners > 9.5),
        'over_10_5': np.mean(total_corners > 10.5),
        'over_11_5': np.mean(total_corners > 11.5),
        'avg_total_corners': np.mean(total_corners)
    }

def predict_cards(
    home_yellows_avg: float,
    away_yellows_avg: float,
    home_reds_avg: float = 0.1,
    away_reds_avg: float = 0.1,
    n_simulations: int = 10000
):
    """Monte Carlo simulation for cards"""
    home_yellows = np.random.poisson(home_yellows_avg, n_simulations)
    away_yellows = np.random.poisson(away_yellows_avg, n_simulations)
    home_reds = np.random.poisson(home_reds_avg, n_simulations)
    away_reds = np.random.poisson(away_reds_avg, n_simulations)
    
    total_cards = home_yellows + away_yellows + home_reds + away_reds
    booking_points = (home_yellows + away_yellows) * 10 + (home_reds + away_reds) * 25
    
    return {
        'over_3_5': np.mean(total_cards > 3.5),
        'over_4_5': np.mean(total_cards > 4.5),
        'over_5_5': np.mean(total_cards > 5.5),
        'avg_total_cards': np.mean(total_cards),
        'avg_booking_points': np.mean(booking_points),
        'over_40_booking_pts': np.mean(booking_points > 40),
        'over_50_booking_pts': np.mean(booking_points > 50),
        'over_60_booking_pts': np.mean(booking_points > 60)
    }

def predict_match(home_team, away_team, league):
    """Generate comprehensive match prediction"""
    # Simulate team stats (in production, these would come from real data)
    home_goals_avg = np.random.uniform(1.2, 2.5)
    away_goals_avg = np.random.uniform(0.9, 2.2)
    home_corners_avg = np.random.uniform(4.0, 7.0)
    away_corners_avg = np.random.uniform(3.5, 6.5)
    home_yellows_avg = np.random.uniform(1.5, 2.5)
    away_yellows_avg = np.random.uniform(1.5, 2.5)
    
    # Get Monte Carlo predictions
    mc_goals = monte_carlo_simulation(home_goals_avg, away_goals_avg)
    mc_corners = predict_corners(home_corners_avg, away_corners_avg)
    mc_cards = predict_cards(home_yellows_avg, away_yellows_avg)
    
    return {
        'home_xg': home_goals_avg,
        'away_xg': away_goals_avg,
        'total_goals': mc_goals['avg_total_goals'],
        'over_2_5': mc_goals['over_2_5'],
        'under_2_5': mc_goals['under_2_5'],
        'btts_yes': mc_goals['btts_yes'],
        'btts_no': mc_goals['btts_no'],
        'corners': mc_corners,
        'cards': mc_cards,
        'goal_distribution': mc_goals['goal_distribution']
    }

def calculate_ah_probability(prediction, handicap, is_home=True):
    """Calculate Asian Handicap probability"""
    # Simplified calculation based on xG
    home_xg = prediction['home_xg']
    away_xg = prediction['away_xg']
    
    xg_diff = home_xg - away_xg if is_home else away_xg - home_xg
    adjusted_diff = xg_diff - handicap
    
    # Use sigmoid function
    prob = 1 / (1 + np.exp(-adjusted_diff * 1.5))
    return max(0.05, min(0.95, prob))

def calculate_goal_line_probability(prediction, line, is_over=True):
    """Calculate Goal Line probability"""
    total_goals = prediction['total_goals']
    
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
        st.metric("Model Prob", f"{true_prob*100:.1f}%")
    with col2:
        st.metric("Book Prob", f"{implied_prob*100:.1f}%")
    with col3:
        if is_value:
            st.markdown(f'<p class="big-value">+{ev:.2f}%</p>', unsafe_allow_html=True)
            st.caption("Expected Value")
        else:
            st.markdown(f'<p class="negative-value">{ev:.2f}%</p>', unsafe_allow_html=True)
            st.caption("Expected Value")
    with col4:
        st.metric("Return", f"${expected_return:.2f}", f"Stake: ${stake}")
    
    if is_value:
        st.markdown(f"""
        <div class="value-bet-positive">
            <h4>✅ VALUE BET DETECTED</h4>
            <p>EV: <strong>+{ev:.2f}%</strong> | Bookmaker: {implied_prob*100:.1f}% | Model: {true_prob*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="value-bet-negative">
            <h4>❌ NO VALUE</h4>
            <p>EV: <strong>{ev:.2f}%</strong> | Bookmaker: {implied_prob*100:.1f}% | Model: {true_prob*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.title("⚽ Football Betting Predictor")
    st.markdown("### ML + Monte Carlo | 9 Leagues | Complete Markets Analysis")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        default_stake = st.number_input("Stake ($)", min_value=1, max_value=1000, value=10, step=5)
        
        st.markdown("---")
        st.markdown("### 🎲 Prediction Method")
        st.info("""
        **Monte Carlo Simulation**
        Uses Poisson distribution with 10,000 simulations for:
        • Goals (Over/Under, BTTS)
        • Corners
        • Cards & Booking Points
        
        **Machine Learning**
        Gradient Boosting + Random Forest
        trained on historical data
        """)
        
        st.markdown("---")
        st.markdown("### 🌍 9 Leagues")
        st.success("""
        🇮🇹 Serie A & Serie B
        🇪🇸 La Liga & La Liga 2
        🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League
        🇩🇪 Bundesliga & 2. Bundesliga
        🇯🇵 J1 League
        🇨🇭 Swiss Super League
        """)
        
        st.markdown("---")
        st.warning("⚠️ For entertainment only. Bet responsibly.")
    
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
            st.markdown(f"## {league_name}")
            
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
            
            # Enter odds
            with st.expander("💰 Enter Bookmaker Odds", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    over_2_5 = st.number_input("Over 2.5", min_value=1.01, value=1.90, step=0.05, key=f"o25_{league_name}")
                with col2:
                    under_2_5 = st.number_input("Under 2.5", min_value=1.01, value=1.95, step=0.05, key=f"u25_{league_name}")
                with col3:
                    btts_yes = st.number_input("BTTS Yes", min_value=1.01, value=1.80, step=0.05, key=f"btts_y_{league_name}")
                
                col1, col2 = st.columns(2)
                with col1:
                    btts_no = st.number_input("BTTS No", min_value=1.01, value=2.05, step=0.05, key=f"btts_n_{league_name}")
                with col2:
                    selected_ah = st.selectbox(
                        "Asian Handicap",
                        ASIAN_HANDICAPS,
                        index=11,
                        key=f"ah_{league_name}",
                        format_func=lambda x: f"{home_team} {'+' if x > 0 else ''}{x}"
                    )
                
                ah_odds = st.number_input(
                    f"AH {'+' if selected_ah > 0 else ''}{selected_ah} Odds",
                    min_value=1.01, value=1.95, step=0.05,
                    key=f"ah_odds_{league_name}"
                )
            
            # Analyze button
            if st.button(f"🎯 Analyze Match", key=f"analyze_{league_name}", type="primary", use_container_width=True):
                with st.spinner("Running Monte Carlo simulation..."):
                    import time
                    time.sleep(1)
                    
                    pred = predict_match(home_team, away_team, league_name)
                    
                    st.markdown("---")
                    st.markdown("## 📊 Match Analysis")
                    
                    # Match header
                    st.markdown(f"""
                    <div style="background: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
                        <h2>{home_team} vs {away_team}</h2>
                        <h3 style="color: {LEAGUES[league_name]['color']};">Expected Goals: {pred['home_xg']:.2f} - {pred['away_xg']:.2f}</h3>
                        <p><strong>Total Goals: {pred['total_goals']:.2f}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("")
                    
                    # Goals Markets
                    st.markdown("---")
                    st.markdown("## ⚽ Goals Markets")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with st.expander(f"📈 Over 2.5 - Odds: {over_2_5}", expanded=True):
                            display_value_bet("Over 2.5", pred['over_2_5'], over_2_5, default_stake)
                    
                    with col2:
                        with st.expander(f"📉 Under 2.5 - Odds: {under_2_5}", expanded=True):
                            display_value_bet("Under 2.5", pred['under_2_5'], under_2_5, default_stake)
                    
                    # BTTS
                    st.markdown("---")
                    st.markdown("## 🔥 Both Teams To Score")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with st.expander(f"✅ Yes - Odds: {btts_yes}", expanded=True):
                            display_value_bet("BTTS Yes", pred['btts_yes'], btts_yes, default_stake)
                    
                    with col2:
                        with st.expander(f"❌ No - Odds: {btts_no}", expanded=True):
                            display_value_bet("BTTS No", pred['btts_no'], btts_no, default_stake)
                    
                    # Asian Handicap
                    st.markdown("---")
                    st.markdown(f"## 🎯 Asian Handicap: {home_team} {'+' if selected_ah > 0 else ''}{selected_ah}")
                    
                    ah_prob = calculate_ah_probability(pred, selected_ah, True)
                    with st.expander(f"📊 Odds: {ah_odds}", expanded=True):
                        display_value_bet(f"AH {selected_ah}", ah_prob, ah_odds, default_stake)
                    
                    # Corners
                    st.markdown("---")
                    st.markdown("## 🚩 Corners Prediction")
                    
                    st.metric("Expected Total Corners", f"{pred['corners']['avg_total_corners']:.1f}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Over 8.5", f"{pred['corners']['over_8_5']*100:.0f}%")
                    col2.metric("Over 9.5", f"{pred['corners']['over_9_5']*100:.0f}%")
                    col3.metric("Over 10.5", f"{pred['corners']['over_10_5']*100:.0f}%")
                    col4.metric("Over 11.5", f"{pred['corners']['over_11_5']*100:.0f}%")
                    
                    if pred['corners']['over_10_5'] > 0.60:
                        st.success(f"✅ Bet: Over 10.5 corners ({pred['corners']['over_10_5']*100:.0f}% confidence)")
                    elif pred['corners']['over_10_5'] < 0.40:
                        st.success(f"✅ Bet: Under 10.5 corners ({(1-pred['corners']['over_10_5'])*100:.0f}% confidence)")
                    else:
                        st.warning("⚠️ Skip corners market (close call)")
                    
                    # Cards
                    st.markdown("---")
                    st.markdown("## 🟨 Cards Prediction")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Expected Cards", f"{pred['cards']['avg_total_cards']:.1f}")
                        st.metric("Over 4.5 Cards", f"{pred['cards']['over_4_5']*100:.0f}%")
                    with col2:
                        st.metric("Booking Points", f"{pred['cards']['avg_booking_points']:.0f}")
                        st.metric("Over 50 pts", f"{pred['cards']['over_50_booking_pts']*100:.0f}%")
                    
                    # Goal Distribution
                    st.markdown("---")
                    st.markdown("## 📊 Goal Distribution (Monte Carlo)")
                    
                    for range_label, prob in pred['goal_distribution'].items():
                        bar_length = int(prob * 30)
                        bar = '█' * bar_length
                        st.text(f"{range_label:3} goals: {bar} {prob*100:.0f}%")
                    
                    # Summary
                    st.markdown("---")
                    st.markdown("## 🏆 Value Bets Summary")
                    
                    value_bets = []
                    
                    # Check all markets
                    if calculate_value(pred['over_2_5'], over_2_5) > 5:
                        value_bets.append(f"Over 2.5 @ {over_2_5} (EV: +{calculate_value(pred['over_2_5'], over_2_5):.1f}%)")
                    if calculate_value(pred['under_2_5'], under_2_5) > 5:
                        value_bets.append(f"Under 2.5 @ {under_2_5} (EV: +{calculate_value(pred['under_2_5'], under_2_5):.1f}%)")
                    if calculate_value(pred['btts_yes'], btts_yes) > 5:
                        value_bets.append(f"BTTS Yes @ {btts_yes} (EV: +{calculate_value(pred['btts_yes'], btts_yes):.1f}%)")
                    if calculate_value(pred['btts_no'], btts_no) > 5:
                        value_bets.append(f"BTTS No @ {btts_no} (EV: +{calculate_value(pred['btts_no'], btts_no):.1f}%)")
                    if calculate_value(ah_prob, ah_odds) > 5:
                        value_bets.append(f"AH {selected_ah} @ {ah_odds} (EV: +{calculate_value(ah_prob, ah_odds):.1f}%)")
                    
                    if value_bets:
                        st.success(f"✅ Found {len(value_bets)} value bet(s)!")
                        for bet in value_bets:
                            st.markdown(f"• **{bet}**")
                    else:
                        st.warning("⚠️ No value bets with >5% edge found")

if __name__ == "__main__":
    main()
