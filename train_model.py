"""
Train ML models for football match prediction

This script will:
1. Load historical match data
2. Engineer features
3. Train XGBoost models
4. Save trained models for the app

Usage:
    python train_model.py --league seria_a --data data/raw/seria_a.csv
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
import pickle
import argparse
import os

class FootballModelTrainer:
    def __init__(self, league_name):
        self.league_name = league_name
        self.model = None
        self.label_encoder = LabelEncoder()
        
    def load_data(self, filepath):
        """Load match data from CSV"""
        print(f"📂 Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        print(f"✅ Loaded {len(df)} matches")
        return df
    
    def engineer_features(self, df):
        """
        Create features for ML model
        
        Features:
        - Recent form (last 5 matches)
        - Goals scored/conceded trends
        - Home/away performance
        - Head-to-head record
        - League position trends
        """
        print("🔧 Engineering features...")
        
        df = df.sort_values('date').reset_index(drop=True)
        features_list = []
        
        for idx, match in df.iterrows():
            home_team = match['home_team']
            away_team = match['away_team']
            match_date = match['date']
            
            # Get recent matches before this match
            recent_matches = df[df['date'] < match_date]
            
            # Home team stats (last 5 matches)
            home_recent = recent_matches[
                (recent_matches['home_team'] == home_team) | 
                (recent_matches['away_team'] == home_team)
            ].tail(5)
            
            # Away team stats (last 5 matches)
            away_recent = recent_matches[
                (recent_matches['home_team'] == away_team) | 
                (recent_matches['away_team'] == away_team)
            ].tail(5)
            
            # Calculate features
            features = {
                # Home team features
                'home_goals_scored_avg': self._avg_goals_scored(home_recent, home_team),
                'home_goals_conceded_avg': self._avg_goals_conceded(home_recent, home_team),
                'home_win_rate': self._win_rate(home_recent, home_team),
                'home_form_points': self._form_points(home_recent, home_team),
                
                # Away team features  
                'away_goals_scored_avg': self._avg_goals_scored(away_recent, away_team),
                'away_goals_conceded_avg': self._avg_goals_conceded(away_recent, away_team),
                'away_win_rate': self._win_rate(away_recent, away_team),
                'away_form_points': self._form_points(away_recent, away_team),
                
                # Head to head
                'h2h_home_wins': self._h2h_wins(recent_matches, home_team, away_team, 'home'),
                'h2h_away_wins': self._h2h_wins(recent_matches, home_team, away_team, 'away'),
                'h2h_draws': self._h2h_draws(recent_matches, home_team, away_team),
                
                # Target variable
                'result': self._get_result(match)
            }
            
            features_list.append(features)
            
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(df)} matches...")
        
        feature_df = pd.DataFrame(features_list)
        
        # Remove rows with missing data (first few matches won't have history)
        feature_df = feature_df.dropna()
        
        print(f"✅ Created {len(feature_df)} training examples with {len(feature_df.columns)-1} features")
        return feature_df
    
    def _avg_goals_scored(self, matches, team):
        """Average goals scored in recent matches"""
        if len(matches) == 0:
            return 1.0  # Default
        
        goals = 0
        for _, match in matches.iterrows():
            if match['home_team'] == team:
                goals += match['home_goals']
            else:
                goals += match['away_goals']
        return goals / len(matches)
    
    def _avg_goals_conceded(self, matches, team):
        """Average goals conceded in recent matches"""
        if len(matches) == 0:
            return 1.0
        
        goals = 0
        for _, match in matches.iterrows():
            if match['home_team'] == team:
                goals += match['away_goals']
            else:
                goals += match['home_goals']
        return goals / len(matches)
    
    def _win_rate(self, matches, team):
        """Win rate in recent matches"""
        if len(matches) == 0:
            return 0.5
        
        wins = 0
        for _, match in matches.iterrows():
            if match['home_team'] == team and match['home_goals'] > match['away_goals']:
                wins += 1
            elif match['away_team'] == team and match['away_goals'] > match['home_goals']:
                wins += 1
        return wins / len(matches)
    
    def _form_points(self, matches, team):
        """Points from recent matches (3 for win, 1 for draw)"""
        if len(matches) == 0:
            return 1.5  # Average
        
        points = 0
        for _, match in matches.iterrows():
            if match['home_team'] == team:
                if match['home_goals'] > match['away_goals']:
                    points += 3
                elif match['home_goals'] == match['away_goals']:
                    points += 1
            else:
                if match['away_goals'] > match['home_goals']:
                    points += 3
                elif match['away_goals'] == match['home_goals']:
                    points += 1
        return points / len(matches)
    
    def _h2h_wins(self, matches, home_team, away_team, side):
        """Head-to-head wins"""
        h2h = matches[
            ((matches['home_team'] == home_team) & (matches['away_team'] == away_team)) |
            ((matches['home_team'] == away_team) & (matches['away_team'] == home_team))
        ].tail(5)
        
        if len(h2h) == 0:
            return 0
        
        wins = 0
        for _, match in h2h.iterrows():
            if side == 'home':
                if match['home_team'] == home_team and match['home_goals'] > match['away_goals']:
                    wins += 1
                elif match['away_team'] == home_team and match['away_goals'] > match['home_goals']:
                    wins += 1
            else:  # away
                if match['home_team'] == away_team and match['home_goals'] > match['away_goals']:
                    wins += 1
                elif match['away_team'] == away_team and match['away_goals'] > match['home_goals']:
                    wins += 1
        return wins
    
    def _h2h_draws(self, matches, home_team, away_team):
        """Head-to-head draws"""
        h2h = matches[
            ((matches['home_team'] == home_team) & (matches['away_team'] == away_team)) |
            ((matches['home_team'] == away_team) & (matches['away_team'] == home_team))
        ].tail(5)
        
        draws = sum(h2h['home_goals'] == h2h['away_goals'])
        return draws
    
    def _get_result(self, match):
        """Get match result (0=Away Win, 1=Draw, 2=Home Win)"""
        if match['home_goals'] > match['away_goals']:
            return 2  # Home win
        elif match['home_goals'] < match['away_goals']:
            return 0  # Away win
        else:
            return 1  # Draw
    
    def train_model(self, feature_df, test_size=0.2):
        """Train XGBoost model"""
        print("🤖 Training model...")
        
        # Separate features and target
        X = feature_df.drop('result', axis=1)
        y = feature_df['result']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"  Training set: {len(X_train)} matches")
        print(f"  Test set: {len(X_test)} matches")
        
        # Train XGBoost
        self.model = xgb.XGBClassifier(
            max_depth=6,
            learning_rate=0.1,
            n_estimators=200,
            objective='multi:softprob',
            num_class=3,
            random_state=42,
            eval_metric='mlogloss'
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        
        print(f"\n📊 Model Performance:")
        print(f"  Training Accuracy: {train_acc:.3f}")
        print(f"  Test Accuracy: {test_acc:.3f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='accuracy')
        print(f"  Cross-val Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
        
        # Detailed report
        print("\n📋 Classification Report:")
        print(classification_report(y_test, test_pred, 
                                   target_names=['Away Win', 'Draw', 'Home Win']))
        
        return self.model
    
    def save_model(self, output_dir='models'):
        """Save trained model"""
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{output_dir}/{self.league_name}_model.pkl"
        
        with open(filename, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"\n💾 Model saved to: {filename}")
        return filename

def main():
    parser = argparse.ArgumentParser(description='Train football prediction model')
    parser.add_argument('--league', type=str, required=True,
                       choices=['seria_a', 'serie_b', 'laliga'],
                       help='League to train model for')
    parser.add_argument('--data', type=str, required=True,
                       help='Path to CSV file with match data')
    parser.add_argument('--output', type=str, default='models',
                       help='Output directory for trained model')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = FootballModelTrainer(args.league)
    
    # Load data
    df = trainer.load_data(args.data)
    
    # Engineer features
    feature_df = trainer.engineer_features(df)
    
    # Train model
    trainer.train_model(feature_df)
    
    # Save model
    trainer.save_model(args.output)
    
    print("\n✅ Training complete!")
    print(f"📝 Next step: Update app.py to load this model instead of using demo predictions")

if __name__ == "__main__":
    main()
