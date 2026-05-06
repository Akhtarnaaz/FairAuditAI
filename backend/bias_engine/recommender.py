"""
Mitigation Recommender — Generates ranked bias mitigation strategies
based on detected bias dimensions and severity.
"""

RECOMMENDATIONS_DB = {
    "data_level": [
        {
            "text": "Collect balanced training data for equal demographic representation.",
            "effort": "high",
            "impact": "very_high",
            "applicable_severity": ["high", "medium"],
        },
        {
            "text": "Assign higher weights to underrepresented groups during training.",
            "effort": "low",
            "impact": "medium",
            "applicable_severity": ["low"],
        },
    ],
    "feature_level": [
        {
            "text": "Remove or anonymize sensitive proxy features like '{feature}'.",
            "effort": "low",
            "impact": "high",
            "applicable_severity": ["high", "medium"],
        },
    ],
    "output_level": [
        {
            "text": "Adjust decision thresholds to equalize acceptance rates.",
            "effort": "low",
            "impact": "medium",
            "applicable_severity": ["high"],
        },
    ],
    "model_level": [
        {
            "text": "Train with fairness-aware loss functions to penalize bias.",
            "effort": "medium",
            "impact": "high",
            "applicable_severity": ["high", "medium"],
        },
    ],
    "best_practice": [
        {
            "text": "Schedule periodic re-audits to detect future fairness drift.",
            "effort": "low",
            "impact": "high",
            "applicable_severity": ["high", "medium", "low"],
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
    Generate up to 4 ranked mitigation recommendations in simple points.
    """
    recommendations = []
    seen_texts = set()
    priority = 1

    # Process dimensions from most biased to least
    sorted_dims = sorted(
        fairness_scores.items(),
        key=lambda x: x[1]["fairness_score"]
    )

    for dim, scores in sorted_dims:
        if len(recommendations) >= 4:
            break
            
        severity = "high" if scores["fairness_score"] < 0.5 else \
                   "medium" if scores["fairness_score"] < 0.8 else "low"

        feature = DIMENSION_FEATURES.get(dim, "input features")

        for rec_type, recs in RECOMMENDATIONS_DB.items():
            if len(recommendations) >= 4:
                break
                
            for rec in recs:
                if severity in rec["applicable_severity"]:
                    text = rec["text"].format(feature=feature)
                    
                    if text not in seen_texts:
                        seen_texts.add(text)
                        recommendations.append({
                            "dimension": dim,
                            "recommendation_type": rec_type,
                            "recommendation_text": text,
                            "effort_level": rec["effort"],
                            "impact_level": rec["impact"],
                            "priority": priority,
                        })
                        priority += 1
                        break # Only one rec per category per dimension to keep it diverse

    return recommendations
