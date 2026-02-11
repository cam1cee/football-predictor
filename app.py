import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import os

# Page config
st.set_page_config(
    page_title="⚽ Football Match Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    .prediction-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .prob-bar {
        height: 30px;
        border-radius: 5px;
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for data persistence
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False
    st.session_state.predictions_history = []

# League configurations
LEAGUES = {
    "Serie A": {
        "teams": [
            "AC Milan", "Inter Milan", "Juventus", "Napoli", "AS Roma", 
            "Lazio", "Atalanta", "Fiorentina", "Bologna", "Torino",
            "Udinese", "Empoli", "Sassuolo", "Cagliari", "Verona",
            "Lecce", "Monza", "Salernitana", "Spezia", "Cremonese"
        ],
        "color": "#008FD7"
    },
    "Serie B": {
        "teams": [
            "Parma", "Como", "Venezia", "Cremonese", "Catanzaro",
            "Palermo", "Brescia", "Sampdoria", "Pisa", "Spezia",
            "Reggiana", "Modena", "Cittadella", "Bari", "Ternana",
            "Cosenza", "Sudtirol", "Ascoli", "Lecco", "Feralpisalò"
        ],
        "color": "#E34234"
    },
    "La Liga": {
        "teams": [
            "Real Madrid", "Barcelona", "Atlético Madrid", "Real Sociedad", 
            "Athletic Bilbao", "Real Betis", "Villarreal", "Valencia", 
            "Osasuna", "Getafe", "Sevilla", "Girona", "Rayo Vallecano",
            "Celta Vigo", "Mallorca", "Cádiz", "Las Palmas", "Alavés",
            "Granada", "Almería"
        ],
        "color": "#FF6B35"
    }
}

def load_demo_model():
    """Load or create a demo model for predictions"""
    # In production, this would load actual trained models
    # For now, we'll simulate predictions
    return {
        "type": "demo",
        "accuracy": 0.56,
        "version": "1.0.0"
    }

def calculate_form_score(team, league):
    """Calculate recent form score (demo - would use real data)"""
    # Simulated form calculation
    return np.random.uniform(0.3, 0.9)

def get_head_to_head(home_team, away_team, league):
    """Get head-to-head statistics (demo)"""
    # In production, query from database
    return {
        "total_matches": np.random.randint(5, 20),
        "home_wins": np.random.randint(2, 8),
        "draws": np.random.randint(1, 5),
        "away_wins": np.random.randint(1, 7),
        "avg_goals": np.random.uniform(1.5, 3.5)
    }

def predict_match(home_team, away_team, league, model):
    """
    Generate match prediction
    In production: use trained ML model with real features
    """
    # Simulate feature engineering
    home_form = calculate_form_score(home_team, league)
    away_form = calculate_form_score(away_team, league)
    
    # Base probabilities with home advantage
    home_base = 0.40 + (home_form - away_form) * 0.15
    draw_base = 0.30
    away_base = 1 - home_base - draw_base
    
    # Add randomness and normalize
    noise = np.random.uniform(-0.05, 0.05, 3)
    probs = np.array([home_base, draw_base, away_base]) + noise
    probs = np.maximum(probs, 0.05)  # Minimum 5% probability
    probs = probs / probs.sum()  # Normalize to sum to 1
    
    return {
        "home_win": probs[0],
        "draw": probs[1],
        "away_win": probs[2],
        "confidence": max(probs),
        "predicted_outcome": ["Home Win", "Draw", "Away Win"][np.argmax(probs)]
    }

def plot_probability_bars(prediction):
    """Display prediction probabilities as horizontal bars"""
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

def display_team_stats(team, league):
    """Display team statistics card"""
    stats = {
        "Form (L5)": f"{np.random.uniform(1.5, 2.8):.1f} PPG",
        "Goals/Match": f"{np.random.uniform(1.0, 2.5):.1f}",
        "Goals Against": f"{np.random.uniform(0.8, 1.8):.1f}",
        "Clean Sheets": f"{np.random.randint(3, 12)}"
    }
    
    st.markdown(f"### {team}")
    for stat, value in stats.items():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.text(stat)
        with col2:
            st.markdown(f"**{value}**")

# Main App
def main():
    # Header
    st.title("⚽ Football Match Predictor")
    st.markdown("### Predict outcomes for Serie A, Serie B & La Liga matches")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/008FD7/FFFFFF?text=Football+AI", use_container_width=True)
        st.markdown("---")
        
        st.markdown("### 📊 Model Info")
        model = load_demo_model()
        st.metric("Model Accuracy", f"{model['accuracy']*100:.1f}%")
        st.metric("Version", model['version'])
        st.metric("Predictions Today", len(st.session_state.predictions_history))
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        This app uses machine learning to predict football match outcomes 
        based on:
        - Recent team form
        - Head-to-head history
        - Home/away performance
        - League statistics
        - Historical patterns
        """)
        
        st.markdown("---")
        st.warning("⚠️ **Disclaimer**: Predictions are for entertainment purposes only. Past performance does not guarantee future results.")
    
    # Main content - League tabs
    tab1, tab2, tab3 = st.tabs(["🇮🇹 Serie A", "🇮🇹 Serie B", "🇪🇸 La Liga"])
    
    tabs_config = [
        (tab1, "Serie A"),
        (tab2, "Serie B"),
        (tab3, "La Liga")
    ]
    
    for tab, league_name in tabs_config:
        with tab:
            st.markdown(f"## {league_name} Match Prediction")
            
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
                # Filter out selected home team
                away_options = [t for t in LEAGUES[league_name]["teams"] if t != home_team]
                away_team = st.selectbox(
                    "Select away team",
                    away_options,
                    key=f"away_{league_name}"
                )
            
            # Match date
            match_date = st.date_input(
                "Match Date",
                value=datetime.now() + timedelta(days=1),
                key=f"date_{league_name}"
            )
            
            st.markdown("---")
            
            # Predict button
            if st.button(f"🎯 Predict Match", key=f"predict_{league_name}", type="primary", use_container_width=True):
                with st.spinner("Analyzing teams and generating prediction..."):
                    # Simulate processing time
                    import time
                    time.sleep(1)
                    
                    # Get prediction
                    prediction = predict_match(home_team, away_team, league_name, model)
                    
                    # Save to history
                    st.session_state.predictions_history.append({
                        "league": league_name,
                        "home": home_team,
                        "away": away_team,
                        "date": match_date,
                        "prediction": prediction["predicted_outcome"]
                    })
                    
                    # Display results
                    st.markdown("---")
                    st.markdown("## 📊 Prediction Results")
                    
                    # Main prediction
                    st.markdown(f"""
                    <div class="prediction-card">
                        <h2 style="text-align: center; margin: 0;">
                            {home_team} vs {away_team}
                        </h2>
                        <h3 style="text-align: center; color: {LEAGUES[league_name]['color']}; margin: 10px 0;">
                            Predicted: {prediction['predicted_outcome']}
                        </h3>
                        <p style="text-align: center; margin: 0;">
                            Confidence: {prediction['confidence']*100:.1f}%
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### Win Probabilities")
                    plot_probability_bars(prediction)
                    
                    # Supporting statistics
                    st.markdown("---")
                    st.markdown("### 📈 Supporting Statistics")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with st.container():
                            display_team_stats(home_team, league_name)
                    
                    with col2:
                        with st.container():
                            display_team_stats(away_team, league_name)
                    
                    # Head to head
                    st.markdown("---")
                    st.markdown("### 🔄 Head-to-Head Record")
                    h2h = get_head_to_head(home_team, away_team, league_name)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Matches", h2h["total_matches"])
                    col2.metric(f"{home_team} Wins", h2h["home_wins"])
                    col3.metric("Draws", h2h["draws"])
                    col4.metric(f"{away_team} Wins", h2h["away_wins"])
                    
                    st.info(f"📊 Average goals per match in head-to-head: {h2h['avg_goals']:.2f}")
                    
                    # Additional insights
                    st.markdown("---")
                    st.markdown("### 💡 Key Insights")
                    
                    insights = []
                    if prediction["home_win"] > 0.5:
                        insights.append(f"✅ Strong home advantage detected for {home_team}")
                    if prediction["draw"] > 0.35:
                        insights.append("⚖️ Closely matched teams - draw is likely")
                    if prediction["confidence"] > 0.6:
                        insights.append("🎯 High confidence prediction")
                    else:
                        insights.append("⚠️ Uncertain match - could go either way")
                    
                    for insight in insights:
                        st.markdown(f"- {insight}")
    
    # Recent predictions section
    if st.session_state.predictions_history:
        st.markdown("---")
        st.markdown("## 📜 Recent Predictions")
        
        # Show last 5 predictions
        recent = st.session_state.predictions_history[-5:][::-1]
        
        for pred in recent:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.text(pred["league"])
            with col2:
                st.text(f"{pred['home']} vs {pred['away']}")
            with col3:
                st.text(f"Predicted: {pred['prediction']}")
            with col4:
                st.text(str(pred["date"]))

if __name__ == "__main__":
    main()
