# ⚽ Football Betting Value Calculator

An advanced Streamlit web application that calculates betting value and finds profitable opportunities across **Serie A**, **La Liga**, **Premier League**, and **J1 League** (2025-26 season).

## 🚀 New Features

### 🎯 Value Bet Calculator
- **Input bookmaker odds** for any market
- **Automatic EV calculation** (Expected Value)
- **Visual indicators** - Green for value bets, Red for no value
- **Expected return calculations** based on your stake

### 📊 Multiple Markets
- **Match Result (1X2)**: Home Win / Draw / Away Win
- **Goals Markets**: Over/Under 2.5 goals
- **Asian Handicaps**: -0.5, +0.5 and more
- **BTTS**: Both Teams to Score
- **Expected Goals**: See predicted xG for both teams

### 🏆 Smart Analysis
- **Total expected goals** for each match
- **Best value bets summary** ranked by EV
- **Probability comparisons** (True vs Implied)
- **Detailed insights** for each match

### 🌍 Updated for 2025-26 Season
- ✅ Serie A - Current teams
- ✅ La Liga - Current teams  
- ✅ Premier League - Current teams
- ✅ J1 League - Current teams

## 📋 Prerequisites

- Python 3.8+ (or use Streamlit Cloud - no installation needed!)
- pip (Python package installer)

## 🛠️ Installation

### Local Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

### Cloud Deployment (Recommended!)

1. **Upload files to GitHub**
2. **Deploy on [Streamlit Cloud](https://share.streamlit.io)**
3. **Your app goes live** with a public URL!

## 🎮 How to Use

### Step 1: Select Teams
Choose your league tab and select home/away teams from the dropdowns

### Step 2: Enter Odds
Input the decimal odds from your bookmaker for:
- Home Win / Draw / Away Win (required)
- Over/Under 2.5 Goals (optional)
- BTTS, Asian Handicaps (optional)

### Step 3: Analyze
Click "Analyze & Find Value Bets" to see:
- **Our predicted probabilities**
- **Expected goals for both teams**
- **Value bet analysis** for each market
- **Best bets summary** ranked by EV

### Step 4: Find Value
Look for **GREEN boxes** = Positive Expected Value = VALUE BET ✅
Avoid **RED boxes** = Negative Expected Value = NO VALUE ❌

## 📊 Understanding the Metrics

### Expected Value (EV)
- **Positive EV (+)**: The bet has long-term profit potential
- **Negative EV (-)**: The bookmaker has an edge
- **Formula**: EV = (True Probability × Odds) - 1

### Implied Probability
- What the bookmaker's odds suggest
- **Formula**: 1 / Decimal Odds
- Example: Odds 2.00 = 50% implied probability

### Expected Return
- Average profit/loss per bet
- Based on your stake amount
- Calculated over many repetitions

## 🎯 Example

**Match**: Barcelona vs Real Madrid
**Bookmaker Odds**: 
- Barcelona Win: 2.10
- Draw: 3.40
- Real Madrid Win: 3.80

**Our Model Predicts**:
- Barcelona: 55% (True probability)
- Draw: 23%
- Real Madrid: 22%

**Analysis**:
- Implied probability (Barcelona @ 2.10): 47.6%
- Our probability: 55%
- **Expected Value**: +15.5% ✅ **VALUE BET!**

## 💰 Betting Markets Explained

### 1X2 (Match Result)
- 1 = Home Win
- X = Draw
- 2 = Away Win

### Over/Under 2.5 Goals
- Over: 3 or more goals scored
- Under: 2 or fewer goals scored

### Asian Handicap -0.5
- Home team starts with -0.5 goal deficit
- Must WIN the match for bet to win
- Higher odds than straight win

### BTTS (Both Teams To Score)
- Yes: Both teams score at least 1 goal
- No: One or both teams fail to score

## 🔧 Configuration

### Change Default Stake
Use the sidebar slider to set your default stake amount ($1-$1000)

### Update Team Lists
Edit `LEAGUES` dictionary in `app.py` if teams change during the season

## 📁 Project Structure

```
football-value-calculator/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── README.md          # This file
├── QUICKSTART.md      # Quick setup guide
├── scraper.py         # Data collection (optional)
└── train_model.py     # Model training (optional)
```

## 🎲 Current Status

**Demo Mode**: The app currently uses simulated predictions based on statistical models.

### To Add Real ML Models:

1. Collect historical match data (3-5 seasons)
2. Train XGBoost/Random Forest models
3. Replace prediction functions with trained models
4. Add real-time data updates

See `train_model.py` and `scraper.py` for implementation guides.

## 🚀 Deployment

### Streamlit Community Cloud (FREE)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy in one click
4. Get public URL instantly

### Self-Hosted
- AWS, Google Cloud, Azure
- Heroku, Railway, Render
- Any platform that supports Python/Streamlit

## 📈 Future Enhancements

- [ ] Real-time odds API integration
- [ ] Historical performance tracking
- [ ] Bankroll management calculator
- [ ] Kelly Criterion stake sizing
- [ ] More Asian Handicap options (-1.5, -2.5, etc.)
- [ ] Correct Score predictions
- [ ] Half-time/Full-time markets
- [ ] Player props (goal scorers, cards)
- [ ] Multi-bet/accumulator optimizer
- [ ] Odds comparison across bookmakers

## ⚠️ Responsible Gambling

**IMPORTANT DISCLAIMERS:**

- This tool is for **educational and entertainment purposes only**
- Predictions are **not guaranteed** and may be inaccurate
- **Never bet more than you can afford to lose**
- Past performance does not guarantee future results
- Gambling can be addictive - seek help if needed
- This is NOT financial advice
- Always verify odds and check betting regulations in your jurisdiction

**Gambling Support:**
- UK: GamCare (0808 8020 133)
- US: National Council on Problem Gambling (1-800-522-4700)
- International: [Gamblers Anonymous](https://www.gamblersanonymous.org)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Better ML models
- More leagues and markets
- Real-time data integration
- UI/UX enhancements
- Performance optimization

## 📄 License

MIT License - Free to use and modify

## 📧 Support

Issues or questions? Check the documentation or open a GitHub issue.

---

**Built with ❤️ using Streamlit, Python, and Machine Learning**

**Remember: Bet responsibly and never chase losses! 🎰**
