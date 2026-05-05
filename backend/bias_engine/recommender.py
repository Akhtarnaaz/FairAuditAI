"""
Mitigation Recommender — Generates ranked bias mitigation strategies
based on detected bias dimensions and severity.
"""

RECOMMENDATIONS_DB = {
    "data_level": [
        {
            "text": "Collect more balanced training data. Source {n}+ examples for each underrepresented demographic group to ensure equal representation.",
            "effort": "high",
            "impact": "very_high",
            "applicable_severity": ["high", "medium"],
        },
        {
            "text": "Re-weight training data. Assign higher sample weights to underrepresented groups during model training to compensate for imbalance.",
            "effort": "low",
            "impact": "medium",
            "applicable_severity": ["high", "medium", "low"],
        },
        {
            "text": "Augment training set with synthetic examples for minority groups using template-based or generative data augmentation techniques.",
            "effort": "medium",
            "impact": "high",
            "applicable_severity": ["high", "medium"],
        },
    ],
    "feature_level": [
        {
            "text": "Remove sensitive proxy features. If '{feature}' is predictive of the protected attribute, remove it or replace with an anonymized identifier.",
            "effort": "low",
            "impact": "high",
            "applicable_severity": ["high", "medium"],
        },
        {
            "text": "Apply fairness constraints during training. Use demographic parity or equalized odds constraints to prevent the model from learning biased patterns.",
            "effort": "medium",
            "impact": "high",
            "applicable_severity": ["high", "medium"],
        },
        {
            "text": "Engineer bias-neutral features. Use dimensionality reduction (PCA) or feature selection to create representations that don't encode demographic information.",
            "effort": "medium",
            "impact": "medium",
            "applicable_severity": ["medium", "low"],
        },
    ],
    "output_level": [
        {
            "text": "Adjust decision thresholds per demographic group. Use different classification thresholds to equalize acceptance rates across groups.",
            "effort": "low",
            "impact": "medium",
            "applicable_severity": ["high", "medium"],
        },
        {
            "text": "Apply post-processing calibration. Adjust model output scores to enforce fairness constraints without retraining the model.",
            "effort": "low",
            "impact": "medium",
            "applicable_severity": ["high", "medium", "low"],
        },
        {
            "text": "Implement continuous monitoring. Track fairness metrics in production and set automated alerts when bias drift is detected.",
            "effort": "medium",
            "impact": "high",
            "applicable_severity": ["high", "medium", "low"],
        },
    ],
    "model_level": [
        {
            "text": "Use adversarial debiasing. Train an adversary network to remove demographic predictability from model representations.",
            "effort": "high",
            "impact": "very_high",
            "applicable_severity": ["high"],
        },
        {
            "text": "Train with fairness-aware loss functions. Add regularization terms that penalize disparate impact during optimization.",
            "effort": "medium",
            "impact": "high",
            "applicable_severity": ["high", "medium"],
        },
    ],
    "best_practice": [
        {
            "text": "Maintain rigorous documentation of model development and data lineage to ensure long-term auditability.",
            "effort": "low",
            "impact": "medium",
            "applicable_severity": ["low"],
        },
        {
            "text": "Schedule periodic re-audits every quarter to detect potential fairness drift as the real-world data distribution changes.",
            "effort": "low",
            "impact": "high",
            "applicable_severity": ["low"],
        },
    ],
}

DIMENSION_FEATURES = {
    "gender": "name/gender",
    "caste": "name/surname",
    "language": "text content",
    "region": "region/location",
}


def generate_recommendations(fairness_scores: dict) -> list[dict]:
    """
    Generate ranked mitigation recommendations.

    Args:
        fairness_scores: Output from calculate_fairness_scores()

    Returns:
        List of recommendation dicts sorted by priority.
    """
    recommendations = []
    priority = 1

    # Process dimensions from most biased to least
    sorted_dims = sorted(
        fairness_scores.items(),
        key=lambda x: x[1]["fairness_score"]
    )

    for dim, scores in sorted_dims:
        severity = "high" if scores["fairness_score"] < 0.5 else \
                   "medium" if scores["fairness_score"] < 0.8 else "low"

        feature = DIMENSION_FEATURES.get(dim, "input features")
        n_samples = max(500, scores.get("sample_size", 500))

        for rec_type, recs in RECOMMENDATIONS_DB.items():
            for rec in recs:
                if severity in rec["applicable_severity"]:
                    text = rec["text"].format(
                        n=n_samples,
                        feature=feature,
                    )
                    recommendations.append({
                        "dimension": dim,
                        "recommendation_type": rec_type,
                        "recommendation_text": text,
                        "effort_level": rec["effort"],
                        "impact_level": rec["impact"],
                        "priority": priority,
                    })
                    priority += 1

    return recommendations
