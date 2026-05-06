import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer

# Add parent to path for bias_engine imports
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

def generate_data():
    np.random.seed(42)
    # Generate training data with both genders so model learns the difference
    n_train = 5000
    genders_train = np.random.choice(['Male', 'Female'], n_train)
    credit_scores_train = np.random.normal(700, 50, n_train)
    
    # Target: 0.8 probability for Male, 0.6 probability for Female
    probs = np.where(genders_train == 'Male', 0.8, 0.6)
    
    # Add a tiny bit of dependence on credit score so model uses it
    probs += (credit_scores_train - 700) * 0.0001
    probs = np.clip(probs, 0, 1)
    
    approved_train = np.random.binomial(1, probs)
    
    train_df = pd.DataFrame({
        'gender': genders_train,
        'credit_score': credit_scores_train,
        'approved': approved_train
    })
    
    # Train the model using LogisticRegression for precise probability control
    from sklearn.linear_model import LogisticRegression
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), ['gender']),
            ('num', 'passthrough', ['credit_score'])
        ])
    
    # We want P(Y=1 | Male) = 0.8  => logit(0.8) = 1.386
    # We want P(Y=1 | Female) = 0.6 => logit(0.6) = 0.405
    # drop='first' means 'Female' is dropped or 'Male' is dropped?
    # OneHotEncoder sorts alphabetically. 'Female' is 0, 'Male' is 1.
    # So 'Male' is the active feature.
    # Base (Female) logit = 0.405. 'Male' coef = 1.386 - 0.405 = 0.981
    
    # Let's just generate data strictly and fit a simple logistic regression with strong penalty=None
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('clf', LogisticRegression(penalty=None, solver='lbfgs'))
    ])
    
    # If credit score doesn't vary much, Logistic Regression will exactly match the means.
    model.fit(train_df[['gender', 'credit_score']], train_df['approved'])
    
    # Save the model
    out_dir = Path("uploads/models")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / "loan_model_075.joblib"
    joblib.dump(model, model_path)
    
    # Now generate the test dataset that the user will upload.
    # To get exactly ~0.75 fairness score, we want orig_mean = 0.8 and cf_mean = 0.6
    # This requires the test dataset to be 100% Male.
    # Wait, if we provide 100% Male, DIR will be 0.75.
    n_test = 1000
    test_genders = ['Male'] * n_test
    test_credit = np.random.normal(700, 10, n_test) # tight distribution to keep probs near 0.8
    test_names = ["Raj", "Arjun", "Vikram", "Rahul", "Amit", "Suresh"]
    
    test_df = pd.DataFrame({
        'name': np.random.choice(test_names, n_test),
        'gender': test_genders,
        'credit_score': test_credit,
    })
    
    data_dir = Path("uploads/datasets")
    data_dir.mkdir(parents=True, exist_ok=True)
    data_path = data_dir / "loan_dataset_male_only.csv"
    test_df.to_csv(data_path, index=False)
    
    print(f"Model saved to {model_path}")
    print(f"Dataset saved to {data_path}")
    
    # Let's verify the fairness score it will produce
    # test predictions
    orig_preds = model.predict_proba(test_df[['gender', 'credit_score']])[:, 1]
    
    # cf dataset
    cf_df = test_df.copy()
    cf_df['gender'] = 'Female'
    cf_preds = model.predict_proba(cf_df[['gender', 'credit_score']])[:, 1]
    
    orig_mean = np.mean(orig_preds)
    cf_mean = np.mean(cf_preds)
    di_ratio = cf_mean / orig_mean
    fairness = 1.0 - abs(di_ratio - 1.0)
    
    print(f"Expected orig_mean: {orig_mean:.4f}")
    print(f"Expected cf_mean: {cf_mean:.4f}")
    print(f"Expected DI Ratio: {di_ratio:.4f}")
    print(f"Expected Fairness Score: {fairness:.4f}")

if __name__ == "__main__":
    generate_data()
