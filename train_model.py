"""
MindCare Model Training Script
Trains stress prediction model with improved ML practices
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import joblib
import logging
import random
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set random seed for reproducibility
RANDOM_STATE = 42
random.seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)

# Model parameters
MODEL_PATH = 'model.pkl'
SCALER_PATH = 'scaler.pkl'
DATASET_PATH = 'stress_dataset.csv'
TEST_SIZE = 0.2
CROSS_VAL_FOLDS = 5


def generate_dataset(n_samples=200):
    """
    Generate synthetic stress dataset with realistic patterns
    
    Args:
        n_samples (int): Number of samples to generate
    
    Returns:
        pd.DataFrame: Generated dataset
    """
    logger.info(f"Generating synthetic dataset with {n_samples} samples...")
    data = []
    
    for _ in range(n_samples):
        sleep = random.uniform(3, 10)
        screen_time = random.uniform(1, 14)
        workload = random.uniform(2, 16)
        
        # Create stress rules with some randomness
        noise = random.uniform(-0.5, 0.5)
        stress_score = 0
        
        # Sleep impact (7-9 hours is ideal)
        if sleep >= 7 and sleep <= 9:
            stress_score -= 1
        elif sleep < 5:
            stress_score += 2
        elif sleep > 10:
            stress_score += 1
        
        # Screen time impact
        if screen_time <= 6:
            stress_score -= 0.5
        elif screen_time > 9:
            stress_score += 1.5
        
        # Workload impact
        if workload <= 8:
            stress_score -= 0.5
        elif workload > 12:
            stress_score += 1.5
        
        # Mood mapping based on stress
        stress_score += noise
        
        if stress_score < 0:
            mood = random.choice([1, 1, 2])  # Happy/Neutral
            stress_level = 0  # Low
        elif stress_score < 1.5:
            mood = random.choice([2, 2, 3])  # Neutral/Sad
            stress_level = 1  # Medium
        else:
            mood = random.choice([3, 3, 4])  # Sad/Stressed
            stress_level = 2  # High
        
        data.append({
            'sleep_hours': round(sleep, 1),
            'screen_time': round(screen_time, 1),
            'workload_hours': round(workload, 1),
            'mood': mood,
            'stress_level': stress_level
        })
    
    df = pd.DataFrame(data)
    logger.info(f"Dataset generated: {len(df)} samples")
    logger.info(f"\nDataset Statistics:\n{df.describe()}")
    
    return df


def load_or_generate_dataset():
    """Load dataset from file or generate new one"""
    if os.path.exists(DATASET_PATH):
        logger.info(f"Loading dataset from {DATASET_PATH}...")
        df = pd.read_csv(DATASET_PATH)
        logger.info(f"Dataset loaded: {len(df)} samples")
    else:
        logger.info(f"Dataset not found. Generating new dataset...")
        df = generate_dataset(n_samples=200)
        df.to_csv(DATASET_PATH, index=False)
        logger.info(f"Dataset saved to {DATASET_PATH}")
    
    return df


def validate_data(df):
    """Validate dataset for quality issues"""
    logger.info("Validating dataset...")
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.any():
        logger.warning(f"Missing values found:\n{missing[missing > 0]}")
        df = df.dropna()
        logger.info(f"Removed rows with missing values. Remaining: {len(df)}")
    
    # Check data types
    logger.info(f"Data types:\n{df.dtypes}")
    
    # Check feature ranges
    logger.info(f"\nFeature ranges:")
    logger.info(f"Sleep: {df['sleep_hours'].min():.1f} - {df['sleep_hours'].max():.1f} hours")
    logger.info(f"Screen time: {df['screen_time'].min():.1f} - {df['screen_time'].max():.1f} hours")
    logger.info(f"Workload: {df['workload_hours'].min():.1f} - {df['workload_hours'].max():.1f} hours")
    
    # Check class distribution
    logger.info(f"\nStress level distribution:\n{df['stress_level'].value_counts().sort_index()}")
    logger.info(f"\nMood distribution:\n{df['mood'].value_counts().sort_index()}")
    
    return df


def train_model(df):
    """
    Train stress prediction model with cross-validation
    
    Args:
        df (pd.DataFrame): Training dataset
    
    Returns:
        tuple: (trained_model, scaler)
    """
    logger.info("\n" + "="*60)
    logger.info("TRAINING MODEL")
    logger.info("="*60)
    
    # Prepare features and target
    X = df[['sleep_hours', 'screen_time', 'workload_hours', 'mood']]
    y = df['stress_level']
    
    # Feature scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    logger.info("Features scaled using StandardScaler")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    logger.info(f"Data split: {len(X_train)} training, {len(X_test)} testing samples")
    
    # Train multiple models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)
    }
    
    best_model = None
    best_score = 0
    best_name = None
    
    for name, model in models.items():
        logger.info(f"\nTraining {name}...")
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=CROSS_VAL_FOLDS)
        logger.info(f"{name} CV Scores: {cv_scores}")
        logger.info(f"{name} CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Train on full training set
        model.fit(X_train, y_train)
        
        # Test predictions
        y_pred = model.predict(X_test)
        y_pred_train = model.predict(X_train)
        
        # Calculate metrics
        test_accuracy = accuracy_score(y_test, y_pred)
        train_accuracy = accuracy_score(y_train, y_pred_train)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        logger.info(f"\n{name} Results:")
        logger.info(f"  Training Accuracy: {train_accuracy:.4f}")
        logger.info(f"  Testing Accuracy:  {test_accuracy:.4f}")
        logger.info(f"  Precision:         {precision:.4f}")
        logger.info(f"  Recall:            {recall:.4f}")
        logger.info(f"  F1-Score:          {f1:.4f}")
        
        logger.info(f"\nConfusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
        logger.info(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")
        
        # Track best model
        if test_accuracy > best_score:
            best_score = test_accuracy
            best_model = model
            best_name = name
    
    logger.info(f"\n{'='*60}")
    logger.info(f"BEST MODEL: {best_name} with {best_score:.4f} accuracy")
    logger.info(f"{'='*60}\n")
    
    return best_model, scaler


def save_model(model, scaler):
    """Save trained model and scaler"""
    try:
        joblib.dump(model, MODEL_PATH)
        logger.info(f"Model saved to {MODEL_PATH}")
        
        joblib.dump(scaler, SCALER_PATH)
        logger.info(f"Scaler saved to {SCALER_PATH}")
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise


def main():
    """Main training pipeline"""
    try:
        logger.info("Starting MindCare Model Training Pipeline")
        logger.info("="*60)
        
        # Load or generate dataset
        df = load_or_generate_dataset()
        
        # Validate data
        df = validate_data(df)
        
        # Train model
        model, scaler = train_model(df)
        
        # Save model
        save_model(model, scaler)
        
        logger.info("\n" + "="*60)
        logger.info("MODEL TRAINING COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Training pipeline failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()