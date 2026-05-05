"""
Bias Detection Engine — Runs model on original + counterfactual inputs
and compares outputs to detect disparities.
"""
import pandas as pd
import numpy as np
from bias_engine.mock_model import MockLoanModel
from bias_engine.counterfactual import generate_counterfactuals


def run_bias_detection(
    original_df: pd.DataFrame,
    dimensions: dict,
    strategy: str = "systematic",
    model=None,
) -> dict:
    """
    Run full bias detection pipeline.

    Returns dict with counterfactual_pairs, predictions, diffs, and dimension_stats.
    """
    if model is None:
        model = MockLoanModel()

    cf_df = generate_counterfactuals(original_df, dimensions, strategy)

    if cf_df.empty:
        return {
            "counterfactual_pairs": pd.DataFrame(),
            "original_predictions": np.array([]),
            "counterfactual_predictions": np.array([]),
            "prediction_diffs": {},
            "num_test_cases": 0,
            "dimension_stats": {},
        }

    data_cols = [c for c in original_df.columns if c in cf_df.columns]

    original_indices = cf_df["original_index"].astype(int).values
    original_subset = original_df.iloc[original_indices].reset_index(drop=True)
    original_indices = cf_df["original_index"].astype(int).values
    original_subset = original_df.iloc[original_indices].reset_index(drop=True)
    
    # ── Detect model's expected features and strip target/extra columns ──
    def _get_model_features(m):
        """Try to extract the feature names the model was trained on."""
        # sklearn Pipeline with BiasPreprocessor
        if hasattr(m, 'named_steps'):
            pre = m.named_steps.get('preprocessor')
            if pre and hasattr(pre, 'train_features_'):
                return list(pre.train_features_)
        # Direct model with feature_names_in_
        if hasattr(m, 'feature_names_in_'):
            return list(m.feature_names_in_)
        return None

    def _align_to_model(m, data):
        """Strip columns the model doesn't expect (e.g. target variables)."""
        expected = _get_model_features(m)
        if expected:
            extra = [c for c in data.columns if c not in expected]
            if extra:
                data = data.drop(columns=extra)
        else:
            # Fallback: drop common target column names
            common_targets = {
                'approved', 'hired', 'priority_treatment', 'claim_approved',
                'admitted', 'shortlisted', 'recidivism_risk_high',
                'priority_high', 'target', 'label', 'y',
            }
            to_drop = [c for c in data.columns if c.lower() in common_targets]
            if to_drop:
                data = data.drop(columns=to_drop)
        return data

    # ── Handle scikit-learn models (predict_proba) vs rule-based (predict) ──
    def get_probs(m, data):
        data = _align_to_model(m, data)
        if hasattr(m, "predict_proba"):
            p = m.predict_proba(data)
            # If binary classifier, take prob of class 1 (usually index 1)
            return p[:, 1] if len(p.shape) > 1 and p.shape[1] > 1 else p
        return m.predict(data)

    original_predictions = get_probs(model, original_subset)

    cf_data = cf_df[data_cols].reset_index(drop=True)
    cf_predictions = get_probs(model, cf_data)


    diffs = np.abs(original_predictions - cf_predictions)

    dimension_stats = {}
    prediction_diffs = {}

    for dim in cf_df["dimension"].unique():
        mask = cf_df["dimension"].values == dim
        dim_diffs = diffs[mask]
        dim_orig = original_predictions[mask]
        dim_cf = cf_predictions[mask]

        prediction_diffs[dim] = dim_diffs.tolist()
        dimension_stats[dim] = {
            "mean_diff": float(np.mean(dim_diffs)),
            "max_diff": float(np.max(dim_diffs)),
            "std_diff": float(np.std(dim_diffs)),
            "num_pairs": int(np.sum(mask)),
            "original_mean": float(np.mean(dim_orig)),
            "counterfactual_mean": float(np.mean(dim_cf)),
            "direction": "lower" if np.mean(dim_cf) < np.mean(dim_orig) else "higher",
        }

    return {
        "counterfactual_pairs": cf_df,
        "original_predictions": original_predictions,
        "counterfactual_predictions": cf_predictions,
        "prediction_diffs": prediction_diffs,
        "num_test_cases": len(cf_df),
        "dimension_stats": dimension_stats,
    }
