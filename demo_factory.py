import os
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

# Add backend to path to use shared utilities
import sys
BASE_DIR = Path("d:/Personal_projects/Detect_bias")
sys.path.append(str(BASE_DIR / "backend"))
from bias_engine.model_utils import BiasPreprocessor

# Output Directory
OUTPUT_DIR = BASE_DIR / "demo_test_suite"
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_demo(domain, filename_prefix, bias_logic):
    print(f"\n--- Generating Demo for: {domain} ---")
    np.random.seed(42)
    n = 300
    
    # 1. Generate Base Features
    if domain == "Loan Approval":
        data = {
            'income': np.random.randint(20000, 150000, n),
            'credit_score': np.random.randint(300, 850, n),
            'loan_amount': np.random.randint(5000, 50000, n),
            'employment_years': np.random.randint(0, 30, n)
        }
        target_name = 'approved'
    elif domain == "Hiring/Recruitment":
        data = {
            'years_exp': np.random.randint(0, 20, n),
            'coding_score': np.random.randint(40, 100, n),
            'education_level': np.random.choice(['Bachelors', 'Masters', 'PhD'], n),
            'previous_salary': np.random.randint(40000, 120000, n)
        }
        target_name = 'hired'
    elif domain == "Healthcare Diagnosis":
        data = {
            'age': np.random.randint(1, 90, n),
            'symptom_severity': np.random.randint(1, 10, n),
            'pre_existing_conditions': np.random.randint(0, 5, n),
            'bmi': np.random.uniform(18, 35, n)
        }
        target_name = 'priority_treatment'
    elif domain == "Insurance Claim":
        data = {
            'claim_amount': np.random.randint(500, 50000, n),
            'policy_years': np.random.randint(1, 15, n),
            'previous_claims': np.random.randint(0, 4, n),
            'annual_income': np.random.randint(30000, 100000, n)
        }
        target_name = 'claim_approved'
    elif domain == "Education Admission":
        data = {
            'entrance_score': np.random.randint(60, 100, n),
            'gpa': np.random.uniform(2.5, 4.0, n),
            'extracurricular_count': np.random.randint(0, 8, n),
            'volunteer_hours': np.random.randint(0, 100, n)
        }
        target_name = 'admitted'

    # 2. Add Sensitive Attributes
    data.update({
        'gender': np.random.choice(['Male', 'Female'], n),
        'caste': np.random.choice(['General', 'OBC', 'SC', 'ST'], n),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n),
        'language': np.random.choice(['English', 'Hindi', 'Tamil', 'Bengali'], n)
    })
    
    df = pd.DataFrame(data)
    
    # 3. Inject Bias and Generate Target
    # bias_logic(df) should return a score/probability
    scores = bias_logic(df)
    # Convert to binary target
    df[target_name] = (scores > np.median(scores)).astype(int)
    
    # 4. Save Dataset
    csv_path = OUTPUT_DIR / f"{filename_prefix}_dataset.csv"
    df.to_csv(csv_path, index=False)
    print(f"Dataset saved: {csv_path}")
    
    # 5. Train Model
    X = df.drop(columns=[target_name])
    y = df[target_name]
    
    model = Pipeline([
        ('preprocessor', BiasPreprocessor()),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    model.fit(X, y)
    
    # 6. Save Model
    model_path = OUTPUT_DIR / f"{filename_prefix}_model.joblib"
    joblib.dump(model, model_path)
    print(f"Model saved: {model_path}")
    
    # 7. Output Stats
    preds = model.predict(X)
    print(f"Accuracy: {accuracy_score(y, preds):.2f}")
    print(f"Sample Predictions: {preds[:10]}")
    
    return df, model

# --- Bias Injection Logics ---

def loan_bias(df):
    # Base: income and credit score
    score = (df['income'] / 10000) + (df['credit_score'] / 100)
    # BIAS: Penalize 'South' region (-3) and 'SC/ST' caste (-4)
    score -= df['region'].map({'South': 3, 'North': 0, 'East': 0, 'West': 0}).fillna(0)
    score -= df['caste'].map({'SC': 4, 'ST': 4, 'OBC': 1, 'General': 0}).fillna(0)
    return score

def hiring_bias(df):
    # Base: exp and coding score
    score = (df['years_exp'] * 2) + (df['coding_score'] / 5)
    # BIAS: Penalize 'Female' gender (-5) and 'Tamil/Bengali' language (-3)
    score -= np.where(df['gender'] == 'Female', 5, 0)
    score -= df['language'].map({'Tamil': 3, 'Bengali': 3, 'English': 0, 'Hindi': 0}).fillna(0)
    return score

def health_bias(df):
    # Base: symptoms and conditions
    score = df['symptom_severity'] * 2 + df['pre_existing_conditions']
    # BIAS: Penalize 'Hindi' language (-4) and 'East' region (-2)
    score -= np.where(df['language'] == 'Hindi', 4, 0)
    score -= np.where(df['region'] == 'East', 2, 0)
    return score

def insurance_bias(df):
    # Base: policy years and income
    score = df['policy_years'] + (df['annual_income'] / 20000)
    # BIAS: Penalize 'SC' caste (-5) and 'Female' gender (-2)
    score -= np.where(df['caste'] == 'SC', 5, 0)
    score -= np.where(df['gender'] == 'Female', 2, 0)
    return score

def education_bias(df):
    # Base: entrance score and gpa
    score = (df['entrance_score'] / 10) + df['gpa']
    # BIAS: Penalize 'ST' caste (-3) and 'West' region (-2)
    score -= np.where(df['caste'] == 'ST', 3, 0)
    score -= np.where(df['region'] == 'West', 2, 0)
    return score

# --- Run Factory ---
if __name__ == "__main__":
    generate_demo("Loan Approval", "loan", loan_bias)
    generate_demo("Hiring/Recruitment", "hiring", hiring_bias)
    generate_demo("Healthcare Diagnosis", "healthcare", health_bias)
    generate_demo("Insurance Claim", "insurance", insurance_bias)
    generate_demo("Education Admission", "education", education_bias)
    
    print(f"\nSuccess! All 5 demo setups are ready in {OUTPUT_DIR}")
