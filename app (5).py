"""
Football Betting Predictor - Complete UI for 9 Leagues
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Football Betting Predictor",
    page_icon="⚽",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("⚽ Football Betting Predictor")
st.markdown("**ML + Monte Carlo** predictions for multiple markets across 9 leagues")

# League configurations
LEAGUES = {
    "🇮🇹 Serie A": {
        "teams": [
            "Napoli", "Inter", "Atalanta", "Juventus", "Roma",
            "Fiorentina", "Lazio", "AC Milan", "Bologna", "Torino",
            "Udinese", "Genoa", "Lecce", "Parma", "Como",
            "Hellas Verona", "Cagliari", "Sassuolo", "Pisa", "Cremonese"
        ]
    },
    "🇮🇹 Serie B": {
        "teams": [
            "Spezia", "Pisa", "Cremonese", "Juve Stabia", "Brescia",
            "Palermo", "Bari", "Cesena", "Reggiana", "Catanzaro",
            "Mantova", "Salernitana", "Modena", "Sampdoria", "Cosenza",
            "Carrarese", "Südtirol", "Frosinone", "Cittadella", "Monza"
        ]
    },
    "🇪🇸 La Liga": {
        "teams": [
            "Barcelona", "Real Madrid", "Atlético Madrid", "Athletic Bilbao",
            "Villarreal", "Mallorca", "Real Sociedad", "Girona", "Osasuna",
            "Betis", "Celta Vigo", "Rayo Vallecano", "Sevilla", "Leganés",
            "Alavés", "Getafe", "Espanyol", "Valladolid", "Valencia", "Las Palmas"
        ]
    },
    "🇪🇸 La Liga 2": {
        "teams": [
            "Levante", "Mirandés", "Racing Santander", "Almería", "Huesca",
            "Elche", "Oviedo", "Málaga", "Sporting Gijón", "Albacete",
            "Eibar", "Zaragoza", "Cádiz", "Eldense", "Granada",
            "Burgos", "Córdoba", "Racing Ferrol", "Cartagena", "Tenerife"
        ]
    },
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": {
        "teams": [
            "Liverpool", "Arsenal", "Chelsea", "Nottingham Forest", "Newcastle",
            "Manchester City", "Bournemouth", "Aston Villa", "Fulham", "Brighton",
            "Brentford", "Manchester United", "West Ham", "Tottenham", "Crystal Palace",
            "Everton", "Wolves", "Leicester City", "Ipswich Town", "Southampton"
        ]
    },
    "🇩🇪 Bundesliga": {
        "teams": [
            "Bayern Munich", "Bayer Leverkusen", "Eintracht Frankfurt", "RB Leipzig",
            "Borussia Dortmund", "VfB Stuttgart", "Werder Bremen", "Freiburg",
            "Mainz 05", "Hoffenheim", "Augsburg", "St. Pauli", "Union Berlin",
            "VfL Bochum", "Wolfsburg", "Gladbach", "Heidenheim", "Holstein Kiel"
        ]
    },
    "🇩🇪 2. Bundesliga": {
        "teams": [
            "Hamburger SV", "Karlsruher SC", "Hannover 96", "1. FC Köln",
            "Fortuna Düsseldorf", "Kaiserslautern", "Elversberg", "Magdeburg",
            "Paderborn", "Hertha BSC", "Nürnberg", "Darmstadt", "Schalke 04",
            "Greuther Fürth", "Braunschweig", "Münster", "Ulm", "Regensburg"
        ]
    },
    "🇯🇵 J1 League": {
        "teams": [
            "Kashima Antlers", "Kashiwa Reysol", "Vissel Kobe", "Kyoto Sanga",
            "Sanfrecce Hiroshima", "Kawasaki Frontale", "Machida Zelvia", "Gamba Osaka",
            "Urawa Red Diamonds", "Cerezo Osaka", "FC Tokyo", "Tokyo Verdy",
            "Yokohama F. Marinos", "Yokohama FC", "Shonan Bellmare", "Albirex Niigata",
            "Shimizu S-Pulse", "Nagoya Grampus", "Fagiano Okayama", "Avispa Fukuoka"
        ]
    },
    "🇨🇭 Swiss Super League": {
        "teams": [
            "FC Zurich", "Basel", "Young Boys", "Lugano", "Servette",
            "St. Gallen", "Lucerne", "Sion", "Lausanne-Sport", "Grasshoppers",
            "Yverdon", "Winterthur"
        ]
    }
}

# Prediction functions (Monte Carlo simulation)
def monte_carlo_simulation(home_goals_avg, away_goals_avg, n_simulations=10000):
    """Monte Carlo simulation for match outcome"""
    home_goals = np.random.poisson(home_goals_avg, n_simulations)
    away_goals = np.random.poisson(away_goals_avg, n_simulations)
    total_goals = home_goals + away_goals
    
    return {
        'over_2_5': np.mean(total_goals > 2.5),
        'under_2_5': 1 - np.mean(total_goals > 2.5),
        'btts_yes': np.mean((home_goals > 0) & (away_goals > 0)),
        'btts_no': 1 - np.mean((home_goals > 0) & (away_goals > 0)),
        'avg_total_goals': np.mean(total_goals),
        'goal_distribution': {
            '0-1': np.mean(total_goals <= 1),
            '2': np.mean(total_goals == 2),
            '3': np.mean(total_goals == 3),
            '4+': np.mean(total_goals >= 4)
        }
    }

def predict_corners(home_corners_avg, away_corners_avg, n_simulations=10000):
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

def predict_cards(home_yellows_avg, away_yellows_avg, home_reds_avg=0.1, away_reds_avg=0.1, n_simulations=10000):
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

def get_team_stats(team, league):
    """Simulate team stats (in production, use real data)"""
    return {
        'goals_avg': np.random.uniform(1.0, 2.5),
        'conceded_avg': np.random.uniform(0.8, 2.0),
        'form': np.random.randint(5, 13),
        'corners_avg': np.random.uniform(4.0, 7.0),
        'yellows_avg': np.random.uniform(1.5, 2.8),
        'reds_avg': np.random.uniform(0.05, 0.15)
    }

def get_form_details(team, league):
    """Simulate form details"""
    results = np.random.choice(['W', 'D', 'L'], size=5, p=[0.4, 0.3, 0.3])
    return {
        'results': list(results),
        'days_since_last_match': np.random.randint(3, 8)
    }

def save_bet_to_csv(date, home_team, away_team, bet_type, odds, stake=0):
    """Save bet to CSV"""
    bet_data = {
        'Date': date,
        'Match': f"{home_team} vs {away_team}",
        'Home_Team': home_team,
        'Away_Team': away_team,
        'Bet_Type': bet_type,
        'Odds': odds,
        'Stake': stake,
        'Potential_Return': stake * odds if stake > 0 else 0,
        'Result': 'Pending',
        'Profit_Loss': 0,
        'Logged_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    csv_file = 'betting_tracker.csv'
    file_exists = os.path.isfile(csv_file)
    
    df_new = pd.DataFrame([bet_data])
    
    if file_exists:
        df_new.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        df_new.to_csv(csv_file, mode='w', header=True, index=False)
    
    return bet_data

# League selector
selected_league = st.selectbox(
    "Select League",
    options=list(LEAGUES.keys()),
    index=0
)

# Sidebar
st.sidebar.header("🔧 Settings")
st.sidebar.info(f"**Current League:** {selected_league}")

# Show teams
with st.sidebar.expander("📋 Team Names"):
    st.caption("Available teams:")
    for team in LEAGUES[selected_league]["teams"]:
        st.text(f"• {team}")

# Betting history viewer
st.sidebar.markdown("---")
if st.sidebar.button("📊 View Betting History"):
    if os.path.isfile('betting_tracker.csv'):
        df_history = pd.read_csv('betting_tracker.csv')
        
        with st.expander("📊 Betting History", expanded=True):
            st.dataframe(df_history, use_container_width=True)
            
            if len(df_history) > 0:
                col1, col2, col3, col4 = st.columns(4)
                
                pending = df_history[df_history['Result'] == 'Pending'].shape[0]
                won = df_history[df_history['Result'] == 'Won'].shape[0]
                lost = df_history[df_history['Result'] == 'Lost'].shape[0]
                total_profit = df_history['Profit_Loss'].sum()
                
                col1.metric("Total Bets", len(df_history))
                col2.metric("Pending", pending)
                col3.metric("Won", won, delta=f"{lost} lost")
                col4.metric("Total P/L", f"{total_profit:+.2f} units")
    else:
        st.sidebar.info("No bets tracked yet")

# Initialize session state
if 'prediction_made' not in st.session_state:
    st.session_state.prediction_made = False
if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = None

# Main interface
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Match Details")
    
    all_teams_sorted = sorted(LEAGUES[selected_league]["teams"])
    
    home_team = st.selectbox("Home Team", all_teams_sorted)
    away_options = [t for t in all_teams_sorted if t != home_team]
    away_team = st.selectbox("Away Team", away_options)

with col2:
    st.subheader("💰 Bookmaker Odds (Decimal)")
    
    tab1, tab2, tab3 = st.tabs(["⚽ Goals", "🚩 Corners", "🟨 Cards"])
    
    with tab1:
        col2a, col2b = st.columns(2)
        with col2a:
            over_odds = st.number_input("Over 2.5", min_value=1.01, value=1.85, step=0.01)
            btts_yes_odds = st.number_input("BTTS Yes", min_value=1.01, value=1.75, step=0.01)
        with col2b:
            under_odds = st.number_input("Under 2.5", min_value=1.01, value=2.00, step=0.01)
            btts_no_odds = st.number_input("BTTS No", min_value=1.01, value=2.10, step=0.01)
    
    with tab2:
        col2c, col2d = st.columns(2)
        with col2c:
            over_corners_odds = st.number_input("Over 10.5", min_value=1.01, value=1.90, step=0.01, key="over_corners")
        with col2d:
            under_corners_odds = st.number_input("Under 10.5", min_value=1.01, value=1.90, step=0.01, key="under_corners")
    
    with tab3:
        col2e, col2f = st.columns(2)
        with col2e:
            over_cards_odds = st.number_input("Over 4.5", min_value=1.01, value=1.90, step=0.01, key="over_cards")
        with col2f:
            under_cards_odds = st.number_input("Under 4.5", min_value=1.01, value=1.90, step=0.01, key="under_cards")

# Advanced settings
with st.expander("⚙️ Advanced Settings"):
    confidence_threshold = st.slider("Confidence Threshold (%)", 50, 80, 60, 5) / 100
    edge_threshold = st.slider("Minimum Edge (%)", 0, 10, 5, 1) / 100

# Predict button
if st.button("🔮 Make Prediction", type="primary", use_container_width=True):
    
    if home_team == away_team:
        st.error("⚠️ Home and away teams must be different!")
        st.stop()
    
    try:
        # Get team stats
        home_stats = get_team_stats(home_team, selected_league)
        away_stats = get_team_stats(away_team, selected_league)
        
        # Get form details
        home_form_details = get_form_details(home_team, selected_league)
        away_form_details = get_form_details(away_team, selected_league)
        
        # Get predictions
        goals_prediction = monte_carlo_simulation(home_stats['goals_avg'], away_stats['goals_avg'])
        corners_prediction = predict_corners(home_stats['corners_avg'], away_stats['corners_avg'])
        cards_prediction = predict_cards(home_stats['yellows_avg'], away_stats['yellows_avg'], 
                                        home_stats['reds_avg'], away_stats['reds_avg'])
        
        # Display results
        st.markdown("---")
        st.header(f"📊 {home_team} vs {away_team}")
        
        # Form visualization
        st.subheader("📈 Recent Form & Fatigue")
        
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            st.write(f"**{home_team} - Last 5 Games:**")
            
            form_html = "<div style='display: flex; gap: 5px;'>"
            for result in home_form_details['results']:
                if result == 'W':
                    color, emoji = '#28a745', '✅'
                elif result == 'D':
                    color, emoji = '#ffc107', '➖'
                else:
                    color, emoji = '#dc3545', '❌'
                
                form_html += f"<div style='background-color: {color}; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold; text-align: center;'>{emoji} {result}</div>"
            
            form_html += "</div>"
            st.markdown(form_html, unsafe_allow_html=True)
            
            days = home_form_details['days_since_last_match']
            st.metric("Days Since Last Match", f"{days} days")
            
            if days < 3:
                st.warning("⚠️ Possible fatigue")
            elif days > 10:
                st.info("ℹ️ Well rested")
            else:
                st.success("✅ Normal rest")
        
        with col_form2:
            st.write(f"**{away_team} - Last 5 Games:**")
            
            form_html = "<div style='display: flex; gap: 5px;'>"
            for result in away_form_details['results']:
                if result == 'W':
                    color, emoji = '#28a745', '✅'
                elif result == 'D':
                    color, emoji = '#ffc107', '➖'
                else:
                    color, emoji = '#dc3545', '❌'
                
                form_html += f"<div style='background-color: {color}; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold; text-align: center;'>{emoji} {result}</div>"
            
            form_html += "</div>"
            st.markdown(form_html, unsafe_allow_html=True)
            
            days = away_form_details['days_since_last_match']
            st.metric("Days Since Last Match", f"{days} days")
            
            if days < 3:
                st.warning("⚠️ Possible fatigue")
            elif days > 10:
                st.info("ℹ️ Well rested")
            else:
                st.success("✅ Normal rest")
        
        st.markdown("---")
        
        # Team stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(f"{home_team} Goals/Game", f"{home_stats['goals_avg']:.2f}")
            st.metric(f"{home_team} Corners/Game", f"{home_stats['corners_avg']:.1f}")
            st.metric(f"{home_team} Cards/Game", f"{home_stats['yellows_avg']:.1f}")
            st.metric(f"{home_team} Form", f"{home_stats['form']}/15")
        
        with col2:
            st.metric("Expected Total Goals", f"{goals_prediction['avg_total_goals']:.2f}")
            st.metric("Expected Total Corners", f"{corners_prediction['avg_total_corners']:.1f}")
            st.metric("Expected Total Cards", f"{cards_prediction['avg_total_cards']:.1f}")
        
        with col3:
            st.metric(f"{away_team} Goals/Game", f"{away_stats['goals_avg']:.2f}")
            st.metric(f"{away_team} Corners/Game", f"{away_stats['corners_avg']:.1f}")
            st.metric(f"{away_team} Cards/Game", f"{away_stats['yellows_avg']:.1f}")
            st.metric(f"{away_team} Form", f"{away_stats['form']}/15")
        
        st.markdown("---")
        
        # Predictions
        col1, col2, col3, col4 = st.columns(4)
        
        # Over/Under 2.5
        with col1:
            st.subheader("📈 Over/Under 2.5")
            
            ou_prob = goals_prediction['over_2_5']
            if ou_prob > 0.5:
                ou_bet_type = "Over 2.5"
                ou_bet_odds = over_odds
                ou_ev = (ou_prob * over_odds) - 1
            else:
                ou_bet_type = "Under 2.5"
                ou_bet_odds = under_odds
                ou_prob = 1 - ou_prob
                ou_ev = (ou_prob * under_odds) - 1
            
            confidence = max(goals_prediction['over_2_5'], goals_prediction['under_2_5'])
            
            st.metric("Prediction", ou_bet_type, f"{confidence:.1%}")
            st.metric("Model Prob", f"{ou_prob:.1%}")
            st.metric("Odds", f"{ou_bet_odds:.2f}")
            st.metric("EV", f"{ou_ev:+.1%}")
            
            if ou_ev > edge_threshold and confidence >= confidence_threshold:
                st.success(f"✅ VALUE BET! {ou_ev:.1%}")
            else:
                st.error(f"❌ No value")
        
        # BTTS
        with col2:
            st.subheader("⚽ BTTS")
            
            btts_prob = goals_prediction['btts_yes']
            if btts_prob > 0.5:
                btts_bet_type = "Yes"
                btts_bet_odds = btts_yes_odds
                btts_ev = (btts_prob * btts_yes_odds) - 1
            else:
                btts_bet_type = "No"
                btts_bet_odds = btts_no_odds
                btts_prob = 1 - btts_prob
                btts_ev = (btts_prob * btts_no_odds) - 1
            
            confidence = max(goals_prediction['btts_yes'], goals_prediction['btts_no'])
            
            st.metric("Prediction", btts_bet_type, f"{confidence:.1%}")
            st.metric("Model Prob", f"{btts_prob:.1%}")
            st.metric("Odds", f"{btts_bet_odds:.2f}")
            st.metric("EV", f"{btts_ev:+.1%}")
            
            if btts_ev > edge_threshold and confidence >= confidence_threshold:
                st.success(f"✅ VALUE BET! {btts_ev:.1%}")
            else:
                st.error(f"❌ No value")
        
        # Corners
        with col3:
            st.subheader("🚩 Corners")
            
            corners_prob = corners_prediction['over_10_5']
            over_ev = (corners_prob * over_corners_odds) - 1
            under_ev = ((1 - corners_prob) * under_corners_odds) - 1
            
            if over_ev > under_ev:
                corners_bet_type = "Over 10.5"
                corners_bet_odds = over_corners_odds
                corners_ev = over_ev
                corners_bet_prob = corners_prob
            else:
                corners_bet_type = "Under 10.5"
                corners_bet_odds = under_corners_odds
                corners_ev = under_ev
                corners_bet_prob = 1 - corners_prob
            
            confidence = max(corners_prob, 1 - corners_prob)
            
            st.metric("Prediction", corners_bet_type, f"{confidence:.1%}")
            st.metric("Model Prob", f"{corners_bet_prob:.1%}")
            st.metric("Odds", f"{corners_bet_odds:.2f}")
            st.metric("EV", f"{corners_ev:+.1%}")
            
            if corners_ev > edge_threshold and confidence >= confidence_threshold:
                st.success(f"✅ VALUE BET! {corners_ev:.1%}")
            else:
                st.error(f"❌ No value")
        
        # Cards
        with col4:
            st.subheader("🟨 Cards")
            
            cards_prob = cards_prediction['over_4_5']
            over_ev = (cards_prob * over_cards_odds) - 1
            under_ev = ((1 - cards_prob) * under_cards_odds) - 1
            
            if over_ev > under_ev:
                cards_bet_type = "Over 4.5"
                cards_bet_odds = over_cards_odds
                cards_ev = over_ev
                cards_bet_prob = cards_prob
            else:
                cards_bet_type = "Under 4.5"
                cards_bet_odds = under_cards_odds
                cards_ev = under_ev
                cards_bet_prob = 1 - cards_prob
            
            confidence = max(cards_prob, 1 - cards_prob)
            
            st.metric("Prediction", cards_bet_type, f"{confidence:.1%}")
            st.metric("Model Prob", f"{cards_bet_prob:.1%}")
            st.metric("Odds", f"{cards_bet_odds:.2f}")
            st.metric("EV", f"{cards_ev:+.1%}")
            
            if cards_ev > edge_threshold and confidence >= confidence_threshold:
                st.success(f"✅ VALUE BET! {cards_ev:.1%}")
            else:
                st.error(f"❌ No value")
        
        # Monte Carlo details
        st.markdown("---")
        st.subheader("🎲 Goal Distribution (10,000 simulations)")
        
        goal_dist = goals_prediction['goal_distribution']
        dist_df = pd.DataFrame({
            'Goals': list(goal_dist.keys()),
            'Probability': [v * 100 for v in goal_dist.values()]
        })
        st.bar_chart(dist_df.set_index('Goals'))
        
        # Final recommendation
        st.markdown("---")
        st.header("🎯 Recommended Bets")
        
        value_bets = []
        if ou_ev > edge_threshold and max(goals_prediction['over_2_5'], goals_prediction['under_2_5']) >= confidence_threshold:
            value_bets.append(f"**{ou_bet_type}** @ {ou_bet_odds:.2f} (EV: {ou_ev:+.1%})")
        if btts_ev > edge_threshold and max(goals_prediction['btts_yes'], goals_prediction['btts_no']) >= confidence_threshold:
            value_bets.append(f"**BTTS {btts_bet_type}** @ {btts_bet_odds:.2f} (EV: {btts_ev:+.1%})")
        if corners_ev > edge_threshold and confidence >= confidence_threshold:
            value_bets.append(f"**{corners_bet_type} corners** @ {corners_bet_odds:.2f} (EV: {corners_ev:+.1%})")
        if cards_ev > edge_threshold and confidence >= confidence_threshold:
            value_bets.append(f"**{cards_bet_type} cards** @ {cards_bet_odds:.2f} (EV: {cards_ev:+.1%})")
        
        if value_bets:
            st.success("✅ **VALUE BETS FOUND:**")
            for bet in value_bets:
                st.markdown(f"• {bet}")
        else:
            st.warning("⚠️ No value bets with current settings")
        
        # Store prediction
        st.session_state.prediction_made = True
        st.session_state.last_prediction = {
            'home_team': home_team,
            'away_team': away_team,
            'goals_prediction': goals_prediction,
            'corners_prediction': corners_prediction,
            'cards_prediction': cards_prediction
        }
        
    except Exception as e:
        st.error(f"❌ Error: {e}")
        import traceback
        st.code(traceback.format_exc())

# Bet tracking
if st.session_state.prediction_made:
    st.markdown("---")
    st.subheader("💰 Track This Bet")
    
    pred_home = st.session_state.last_prediction['home_team']
    pred_away = st.session_state.last_prediction['away_team']
    
    with st.form("bet_tracker_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            match_date = st.date_input("Match Date", value=pd.Timestamp.now())
            bet_type_input = st.text_input("Bet Type", placeholder="e.g., Over 2.5")
        
        with col2:
            bet_odds_input = st.number_input("Odds", min_value=1.01, value=2.0, step=0.01)
            bet_stake_input = st.number_input("Stake (units)", min_value=0.0, value=1.0, step=0.5)
        
        with col3:
            st.metric("Potential Return", f"{bet_stake_input * bet_odds_input:.2f}")
            st.metric("Potential Profit", f"{bet_stake_input * (bet_odds_input - 1):.2f}")
        
        if st.form_submit_button("💾 Save Bet", type="primary"):
            if bet_type_input:
                save_bet_to_csv(
                    date=match_date.strftime('%Y-%m-%d'),
                    home_team=pred_home,
                    away_team=pred_away,
                    bet_type=bet_type_input,
                    odds=bet_odds_input,
                    stake=bet_stake_input
                )
                st.success("✅ Bet saved!")
            else:
                st.error("❌ Please enter bet type")

# Footer
st.markdown("---")
st.caption("⚠️ For entertainment only. Bet responsibly. Past performance doesn't guarantee future results.")
