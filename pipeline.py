import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import joblib
import os
import sys

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kidney_model.joblib")

# ── Location → Water Sodium Mapping (mg/L) ──────────────────────────────────
# Based on published water quality surveys per region.
LOCATION_WATER_SODIUM = {
    # River Nile Governorates (Freshwater: ~0.3 ppt)
    "River Nile - Cairo": 300,
    "River Nile - Giza": 300,
    "River Nile - Qalyubia": 300,
    "River Nile - Menofia": 300,
    "River Nile - Gharbia": 300,
    "River Nile - Dakahlia": 300,
    "River Nile - Monufia": 300,
    "River Nile - Sharqia": 300,
    "River Nile - Qena": 300,
    "River Nile - Sohag": 300,
    "River Nile - Assiut": 300,
    "River Nile - Minya": 300,
    "River Nile - Beni Suef": 300,
    "River Nile - Fayoum": 300,
    "River Nile - Luxor": 300,
    "River Nile - Aswan": 300,
    
    # Mediterranean Coastal Governorates (Brackish & Marine: 1-15 ppt)
    "Mediterranean - Alexandria": 5500,
    "Mediterranean - Beheira": 5500,
    "Mediterranean - Kafr El-Sheikh": 6000,
    "Mediterranean - Damietta": 6000,
    "Mediterranean - Port Said": 10000,
    
    # Red Sea & Gulf Governorates (High Marine Salinity: 40-42 ppt)
    "Red Sea - Red Sea": 40500,
    "Red Sea - South Sinai": 40500,
    "Red Sea - Suez": 41000,
    "Red Sea - Ismailia": 41000,
    
    # Desert & Oasis Governorates (Deep Groundwater)
    "Desert - New Valley": 550,
    "Desert - Matrouh": 5000,
    "Desert - North Sinai": 6500
}

def get_sodium_for_location(location: str) -> float:
    """Return water sodium level (mg/L) for a given location string."""
    if location in LOCATION_WATER_SODIUM:
        return float(LOCATION_WATER_SODIUM[location])
    # Fuzzy match: check if any key contains the search term
    location_lower = location.lower()
    for key, val in LOCATION_WATER_SODIUM.items():
        if location_lower in key.lower() or key.lower() in location_lower:
            return float(val)
    # Default: world average tap water sodium
    return 80.0

def get_sodium_risk_level(sodium: float) -> dict:
    """Classify water sodium level into a risk category with details."""
    if sodium <= 50:
        return {"level": "Safe", "color": "#10b981", "score": 0.1, "description": "Excellent water quality. Very low sodium — no kidney stress from water source."}
    elif sodium <= 120:
        return {"level": "Low Risk", "color": "#22d3ee", "score": 0.25, "description": "Acceptable sodium levels. Minimal additional kidney burden."}
    elif sodium <= 200:
        return {"level": "Moderate", "color": "#f59e0b", "score": 0.5, "description": "Elevated sodium in water. May contribute to higher blood pressure and increased calcium excretion."}
    elif sodium <= 300:
        return {"level": "High Risk", "color": "#f97316", "score": 0.75, "description": "High sodium water. Significantly increases kidney stone risk and cardiovascular strain."}
    else:
        return {"level": "Dangerous", "color": "#ef4444", "score": 0.95, "description": "Dangerously high sodium. Major risk factor for kidney stones, hypertension, and kidney failure progression."}


def generate_large_synthetic_data(n_per_class=20000):
    """Generate 120k+ samples with Gender, Smoker, Water_Sodium features."""
    np.random.seed(42)
    
    # ─── Class 0: Healthy ────────────────────────────────────────────────
    n = n_per_class
    gender_0 = np.random.binomial(1, 0.50, n)  # balanced
    smoker_0 = np.random.binomial(1, 0.15, n)  # low smoker rate
    age_0 = np.random.uniform(20, 50, n)
    # Gender-adjusted creatinine: males ~0.95, females ~0.75
    creat_0 = np.where(gender_0 == 1, np.random.normal(0.95, 0.1, n), np.random.normal(0.75, 0.08, n))
    ucal_0 = np.random.normal(140, 30, n)
    uph_0 = np.random.normal(6.8, 0.3, n)
    uacid_0 = np.random.normal(4.8, 0.4, n)
    sodium_0 = np.random.normal(60, 25, n).clip(10, 200)  # mostly low-sodium areas

    # ─── Class 1: Suspected Kidney Dysfunction ───────────────────────────
    gender_1 = np.random.binomial(1, 0.55, n)  # slight male bias
    smoker_1 = np.random.binomial(1, 0.35, n)  # moderate smoker rate
    age_1 = np.random.uniform(40, 65, n)
    creat_1 = np.where(gender_1 == 1, np.random.normal(2.1, 0.4, n), np.random.normal(1.8, 0.35, n))
    ucal_1 = np.random.normal(160, 20, n)
    uph_1 = np.random.normal(6.4, 0.4, n)
    uacid_1 = np.random.normal(5.0, 0.5, n)
    sodium_1 = np.random.normal(130, 40, n).clip(10, 400)

    # ─── Class 2: Severe Kidney Failure ──────────────────────────────────
    gender_2 = np.random.binomial(1, 0.65, n)  # strong male bias
    smoker_2 = np.random.binomial(1, 0.55, n)  # high smoker rate
    age_2 = np.random.uniform(60, 85, n)
    creat_2 = np.where(gender_2 == 1, np.random.normal(6.8, 1.0, n), np.random.normal(6.0, 0.9, n))
    ucal_2 = np.random.normal(150, 15, n)
    uph_2 = np.random.normal(6.4, 0.3, n)
    uacid_2 = np.random.normal(5.4, 0.3, n)
    sodium_2 = np.random.normal(200, 60, n).clip(10, 500)

    # ─── Class 3: Uric Acid Stones Risk ──────────────────────────────────
    gender_3 = np.random.binomial(1, 0.70, n)  # strong male bias
    smoker_3 = np.random.binomial(1, 0.40, n)
    age_3 = np.random.uniform(30, 60, n)
    creat_3 = np.where(gender_3 == 1, np.random.normal(1.15, 0.1, n), np.random.normal(0.95, 0.08, n))
    ucal_3 = np.random.normal(270, 30, n)
    uph_3 = np.random.normal(5.3, 0.2, n)
    uacid_3 = np.random.normal(7.8, 0.4, n)
    sodium_3 = np.random.normal(220, 50, n).clip(10, 500)

    # ─── Class 4: Calcium Stones Risk ────────────────────────────────────
    gender_4 = np.random.binomial(1, 0.60, n)
    smoker_4 = np.random.binomial(1, 0.25, n)
    age_4 = np.random.uniform(30, 60, n)
    creat_4 = np.where(gender_4 == 1, np.random.normal(1.05, 0.1, n), np.random.normal(0.85, 0.08, n))
    ucal_4 = np.random.normal(360, 40, n)
    uph_4 = np.random.normal(6.7, 0.3, n)
    uacid_4 = np.random.normal(5.5, 0.4, n)
    # High sodium water is a DIRECT trigger for calcium stones
    sodium_4 = np.random.normal(310, 60, n).clip(50, 550)

    # ─── Class 5: Multiple Stone Risk ────────────────────────────────────
    gender_5 = np.random.binomial(1, 0.68, n)
    smoker_5 = np.random.binomial(1, 0.50, n)
    age_5 = np.random.uniform(35, 65, n)
    creat_5 = np.where(gender_5 == 1, np.random.normal(1.35, 0.2, n), np.random.normal(1.15, 0.15, n))
    ucal_5 = np.random.normal(240, 25, n)
    uph_5 = np.random.normal(5.5, 0.2, n)
    uacid_5 = np.random.normal(7.1, 0.3, n)
    sodium_5 = np.random.normal(270, 55, n).clip(30, 500)

    df = pd.DataFrame({
        'Age':           np.concatenate([age_0, age_1, age_2, age_3, age_4, age_5]),
        'Gender':        np.concatenate([gender_0, gender_1, gender_2, gender_3, gender_4, gender_5]),
        'Smoker':        np.concatenate([smoker_0, smoker_1, smoker_2, smoker_3, smoker_4, smoker_5]),
        'Creatinine':    np.concatenate([creat_0, creat_1, creat_2, creat_3, creat_4, creat_5]),
        'Urine_Calcium': np.concatenate([ucal_0, ucal_1, ucal_2, ucal_3, ucal_4, ucal_5]),
        'Urine_pH':      np.concatenate([uph_0, uph_1, uph_2, uph_3, uph_4, uph_5]),
        'Uric_Acid':     np.concatenate([uacid_0, uacid_1, uacid_2, uacid_3, uacid_4, uacid_5]),
        'Water_Sodium':  np.concatenate([sodium_0, sodium_1, sodium_2, sodium_3, sodium_4, sodium_5]),
    })
    
    labels = np.array([0]*n + [1]*n + [2]*n + [3]*n + [4]*n + [5]*n)
    return df, labels


def calculate_ratios(df):
    """Compute engineered feature ratios from raw features."""
    df_processed = df.copy()
    df_processed['Ca_Cr_Ratio'] = df_processed['Urine_Calcium'] / (df_processed['Creatinine'] + 1e-8)
    df_processed['Ua_Cr_Ratio'] = df_processed['Uric_Acid'] / (df_processed['Creatinine'] + 1e-8)
    df_processed['Sodium_Cr_Interaction'] = df_processed['Water_Sodium'] * df_processed['Creatinine']
    return df_processed


def train_model():
    """Train the 6-class XGBoost model with expanded features."""
    print("=" * 60)
    print("  KIDNEY DIAGNOSTIC MODEL — FULL RETRAINING")
    print("  Features: Age, Gender, Smoker, Creatinine,")
    print("            Urine Calcium, Urine pH, Uric Acid,")
    print("            Water Sodium + 3 Engineered Ratios")
    print("=" * 60)
    print("\nGenerating 120,000 synthetic samples (20k per class)...")
    X, y = generate_large_synthetic_data(20000)
    
    # Save the generated synthetic scenarios to a CSV file
    dataset_df = X.copy()
    dataset_df['Label'] = y
    dataset_df.to_csv('synthetic_scenarios_dataset.csv', index=False)
    print("Saved generated scenarios to 'synthetic_scenarios_dataset.csv'.")
    
    X_processed = calculate_ratios(X)
    
    print(f"Total features: {X_processed.shape[1]}")
    print(f"Feature names: {list(X_processed.columns)}")
    
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)
    
    print(f"\nTraining set: {X_train.shape[0]} | Test set: {X_test.shape[0]}")
    print("Training 6-class XGBoost model (expanded)...")
    
    model = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=6,
        max_depth=5,
        n_estimators=150,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        n_jobs=-1,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    accuracy = model.score(X_test, y_test)
    print(f"\nTest Accuracy: {accuracy:.4f}")
    
    # Feature importances
    importances = model.feature_importances_
    feature_names = X_processed.columns.tolist()
    print("\nFeature Importances:")
    for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
        bar = "#" * int(imp * 50)
        print(f"  {name:25s} {imp:.4f} {bar}")
    
    # Save
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")
    print("=" * 60)
    return model


def load_or_train_model():
    """Load model from disk if available, otherwise train and save."""
    if os.path.exists(MODEL_PATH):
        print(f"Loading pre-trained model from {MODEL_PATH}...")
        return joblib.load(MODEL_PATH)
    else:
        print("No saved model found. Training a new model...")
        return train_model()

model = load_or_train_model()

FEATURE_ORDER = [
    'Age', 'Gender', 'Smoker', 'Creatinine',
    'Urine_Calcium', 'Urine_pH', 'Uric_Acid', 'Water_Sodium',
    'Ca_Cr_Ratio', 'Ua_Cr_Ratio', 'Sodium_Cr_Interaction'
]

def predict_risk(age: float, gender: int, smoker: int, creatinine: float,
                 urine_calcium: float = None, urine_ph: float = None,
                 uric_acid: float = None, water_sodium: float = 80.0) -> dict:
    """Run prediction with the expanded feature set."""
    safe_urine_calcium = urine_calcium if urine_calcium is not None else np.nan
    safe_urine_ph = urine_ph if urine_ph is not None else np.nan
    safe_uric_acid = uric_acid if uric_acid is not None else np.nan

    ca_cr_ratio = safe_urine_calcium / (creatinine + 1e-8) if not pd.isna(safe_urine_calcium) else np.nan
    ua_cr_ratio = safe_uric_acid / (creatinine + 1e-8) if not pd.isna(safe_uric_acid) else np.nan
    sodium_cr = water_sodium * creatinine
    
    features = pd.DataFrame({
        'Age': [age],
        'Gender': [gender],
        'Smoker': [smoker],
        'Creatinine': [creatinine],
        'Urine_Calcium': [safe_urine_calcium],
        'Urine_pH': [safe_urine_ph],
        'Uric_Acid': [safe_uric_acid],
        'Water_Sodium': [water_sodium],
        'Ca_Cr_Ratio': [ca_cr_ratio],
        'Ua_Cr_Ratio': [ua_cr_ratio],
        'Sodium_Cr_Interaction': [sodium_cr]
    })
    
    # Ensure column order matches training
    features = features[FEATURE_ORDER]
    
    prediction = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0].tolist()
    return {
        'prediction_class': prediction,
        'probabilities': probabilities
    }


# ── CLI entry point for retraining ───────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--retrain":
        # Force retrain even if model exists
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
    train_model()
