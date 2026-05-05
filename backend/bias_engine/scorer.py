"""
Fairness Scorer — Calculates normalized fairness metrics using
Disparate Impact Ratio and Demographic Parity.
"""
import numpy as np


def calculate_fairness_scores(dimension_stats: dict) -> dict:
    """
    Calculate fairness scores for each dimension.

    Args:
        dimension_stats: Output from run_bias_detection()["dimension_stats"]

    Returns:
        {dimension: {fairness_score, disparity_ratio, demographic_parity_diff, status, ...}}
    """
    results = {}

    for dim, stats in dimension_stats.items():
        orig_mean = stats["original_mean"]
        cf_mean = stats["counterfactual_mean"]

        # Disparate Impact Ratio: minority_rate / majority_rate
        if orig_mean > 0:
            di_ratio = cf_mean / orig_mean
        else:
            di_ratio = 1.0

        # Clamp ratio to reasonable range
        di_ratio = max(0.0, min(di_ratio, 2.0))

        # Fairness Score = 1 - |DIRatio - 1.0| (clamped 0-1)
        fairness_score = max(0.0, min(1.0, 1.0 - abs(di_ratio - 1.0)))

        # Demographic parity difference
        dp_diff = abs(orig_mean - cf_mean)

        # Confidence interval (simple bootstrap-like estimate)
        std = stats["std_diff"]
        n = stats["num_pairs"]
        margin = 1.96 * std / max(np.sqrt(n), 1)

        # Status classification
        if fairness_score >= 0.8:
            status = "fair"
        elif fairness_score >= 0.5:
            status = "review"
        else:
            status = "biased"

        results[dim] = {
            "fairness_score": round(fairness_score, 4),
            "disparity_ratio": round(di_ratio, 4),
            "demographic_parity_diff": round(dp_diff, 4),
            "confidence_lower": round(max(0, fairness_score - margin), 4),
            "confidence_upper": round(min(1, fairness_score + margin), 4),
            "sample_size": n,
            "status": status,
            "mean_diff": round(stats["mean_diff"], 4),
            "direction": stats["direction"],
        }

    return results


def calculate_overall_score(fairness_scores: dict) -> float:
    """Calculate weighted overall fairness score."""
    if not fairness_scores:
        return 0.0
    scores = [v["fairness_score"] for v in fairness_scores.values()]
    return round(float(np.mean(scores)), 4)
