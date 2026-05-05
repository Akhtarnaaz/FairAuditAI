"""
Shared utilities for model preprocessing and wrapping.
Used during model training and inference (audits).
"""
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder

class BiasPreprocessor(BaseEstimator, TransformerMixin):
    """
    Simple preprocessor that LabelEncodes strings and fills NAs.
    """
    def __init__(self, exclude_cols=None):
        self.exclude_cols = exclude_cols or []
        self.encoders = {}

    def fit(self, X, y=None):
        self.train_features_ = list(X.columns)
        for col in X.columns:
            if col not in self.exclude_cols and X[col].dtype == 'object':
                le = LabelEncoder()
                le.fit(X[col].astype(str))
                self.encoders[col] = le
        return self
    
    def transform(self, X):
        X_copy = X.copy()
        
        # Align features with training data to drop target vars and add missing ones
        if hasattr(self, 'train_features_'):
            extra_cols = [c for c in X_copy.columns if c not in self.train_features_]
            if extra_cols:
                X_copy = X_copy.drop(columns=extra_cols)
            missing_cols = [c for c in self.train_features_ if c not in X_copy.columns]
            for c in missing_cols:
                X_copy[c] = 0
                
        for col, le in self.encoders.items():
            if col in X_copy.columns:
                # Handle unknown labels by mapping to a default
                X_copy[col] = X_copy[col].astype(str).map(lambda x: x if x in le.classes_ else le.classes_[0])
                X_copy[col] = le.transform(X_copy[col])
        
        # Drop excluded or remaining objects
        cols_to_drop = [col for col in X_copy.columns if X_copy[col].dtype == 'object']
        X_copy = X_copy.drop(columns=cols_to_drop)
        
        # Ensure final column order matches exactly what was kept during training
        if hasattr(self, 'train_features_'):
            final_features = [c for c in self.train_features_ if c in X_copy.columns]
            X_copy = X_copy[final_features]
            
        return X_copy.fillna(0)

class NeutralWrapper:
    """
    Wrapper for models trained on subset of features.
    Drops sensitive columns during inference to match training schema.
    """
    def __init__(self, model, dropped_cols):
        self.model = model
        self.dropped_cols = dropped_cols
    
    def predict(self, df):
        df_clean = df.drop(columns=[c for c in self.dropped_cols if c in df.columns], errors='ignore')
        return self.model.predict(df_clean)
    
    def predict_proba(self, df):
        df_clean = df.drop(columns=[c for c in self.dropped_cols if c in df.columns], errors='ignore')
        return self.model.predict_proba(df_clean)
