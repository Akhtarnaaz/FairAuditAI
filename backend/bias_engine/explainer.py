"""
Explanation Generator — Produces plain-language bias explanations
with root cause analysis, severity, and legal implications.
"""


DIMENSION_LABELS = {
    "gender": "Gender",
    "caste": "Caste/Identity",
    "language": "Language",
    "region": "Region",
}

LEGAL_IMPLICATIONS = {
    "gender": "This may violate the Equal Credit Opportunity Act (ECOA) and Title VII of the Civil Rights Act, which prohibit discrimination based on sex.",
    "caste": "Caste-based discrimination violates the Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989, and constitutional provisions under Article 15.",
    "language": "Language-based disparate treatment may violate anti-discrimination policies and inclusivity mandates in public services.",
    "region": "Regional bias may constitute geographic discrimination and violate equal opportunity principles in lending and employment.",
}

ROOT_CAUSES = {
    "high": {
        "gender": "Training data likely contains significant gender imbalance with more positive outcomes for male applicants. The model has learned a spurious correlation between gender indicators and approval.",
        "caste": "Training data reflects historical societal discrimination. Surnames correlated with caste carry predictive weight for outcomes, embedding systemic bias.",
        "language": "Model performance degrades for non-English inputs due to underrepresentation in training data. Tokenization and feature extraction favor English text.",
        "region": "Training data is geographically skewed. Certain regions are underrepresented, causing the model to associate geography with outcomes.",
    },
    "medium": {
        "gender": "Moderate gender signal detected in model features. Some input features may serve as gender proxies (e.g., name patterns).",
        "caste": "Name-based features carry moderate caste signal. The model partially relies on surname patterns that correlate with caste identity.",
        "language": "Minor performance gap for non-English content. The model handles multilingual input inconsistently.",
        "region": "Some geographic features carry regional bias. The model shows preference for regions better represented in training data.",
    },
    "low": {
        "gender": "Minimal gender bias detected. The model treats gender-variant inputs largely equally with minor statistical variation.",
        "caste": "Low caste-based disparity. Name-based features show minimal correlation with outcomes across caste groups.",
        "language": "Negligible language-based performance gap. The model handles linguistic variation adequately.",
        "region": "Minor regional variation within acceptable bounds. Geographic features have minimal impact on predictions.",
    },
}


def generate_explanations(fairness_scores: dict, dimension_stats: dict) -> list[dict]:
    """
    Generate plain-language explanations for each biased dimension.

    Args:
        fairness_scores: Output from calculate_fairness_scores()
        dimension_stats: Output from run_bias_detection()["dimension_stats"]

    Returns:
        List of explanation dicts with text, root_cause, severity, legal implications.
    """
    explanations = []

    for dim, scores in fairness_scores.items():
        fs = scores["fairness_score"]
        stats = dimension_stats.get(dim, {})
        label = DIMENSION_LABELS.get(dim, dim.title())

        # Determine severity
        if fs < 0.5:
            severity = "high"
        elif fs < 0.8:
            severity = "medium"
        else:
            severity = "low"

        bias_pct = round((1 - fs) * 100)
        mean_diff = round(scores.get("mean_diff", 0) * 100, 1)
        direction = stats.get("direction", "lower")

        # Build explanation text
        if severity == "high":
            text = (
                f"The model shows {bias_pct}% bias in the {label} dimension. "
                f"For identical input contexts, the disadvantaged group receives "
                f"scores that are {mean_diff}% {direction} on average. "
                f"This represents a significant disparity that requires immediate attention. "
                f"The Disparate Impact Ratio is {scores['disparity_ratio']:.2f}, "
                f"which falls well below the 0.80 threshold (the '80% rule')."
            )
        elif severity == "medium":
            text = (
                f"Moderate bias detected in the {label} dimension ({bias_pct}% bias). "
                f"The disadvantaged group shows {mean_diff}% {direction} prediction scores "
                f"compared to the baseline group. "
                f"The Disparate Impact Ratio is {scores['disparity_ratio']:.2f}, "
                f"which is near but may not meet the 0.80 fairness threshold."
            )
        else:
            text = (
                f"Minimal bias detected in the {label} dimension. "
                f"The fairness score of {fs:.2f} indicates the model treats "
                f"demographic variants largely equally, with only {mean_diff}% average difference. "
                f"The Disparate Impact Ratio of {scores['disparity_ratio']:.2f} meets the 0.80 threshold."
            )

        root_cause = ROOT_CAUSES.get(severity, {}).get(dim, "Unable to determine root cause.")
        legal = LEGAL_IMPLICATIONS.get(dim, "Consult legal counsel for jurisdiction-specific implications.")

        explanations.append({
            "dimension": dim,
            "explanation_text": text,
            "root_cause": root_cause,
            "severity": severity,
            "affected_metric": f"Approval score ({mean_diff}% difference)",
            "legal_implications": legal if severity in ("high", "medium") else "No immediate legal concern at this bias level.",
        })

    # Sort by severity (high first)
    severity_order = {"high": 0, "medium": 1, "low": 2}
    explanations.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return explanations
