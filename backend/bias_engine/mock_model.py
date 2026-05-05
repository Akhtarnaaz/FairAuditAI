"""
Mock Model — A deliberately biased loan approval model for demo/testing.

This model introduces controlled bias across gender, caste, and region
to produce visually clear bias results during demo.
"""
import numpy as np
import pandas as pd


class MockLoanModel:
    """
    A fake loan approval model that deliberately introduces bias.

    Base approval is calculated from income + credit_score.
    Bias is introduced by penalizing:
      - Female applicants: -15% score
      - Low-caste surnames: -20% score
      - Southern region: -18% score
    """

    BIAS_WEIGHTS = {
        "gender_female": -0.15,
        "caste_low": -0.20,
        "region_south": -0.18,
        "language_non_english": -0.08,
    }

    LOW_CASTE_SURNAMES = {
        "paswan", "chamar", "valmiki", "dhobi", "khatik", "musahar",
        "jatav", "raidas", "madiga", "paraiah", "mahar", "mang",
        "hela", "dom", "bhangi",
    }

    SOUTH_LOCATIONS = {
        "chennai", "bangalore", "hyderabad", "kochi", "coimbatore",
        "thiruvananthapuram", "madurai", "visakhapatnam", "mysore",
        "mangalore", "tirupati", "vijayawada",
    }

    FEMALE_NAMES = {
        "priya", "anita", "sunita", "kavita", "neha", "pooja", "ritu",
        "meera", "lakshmi", "geeta", "sonal", "anjali", "divya", "sneha",
        "nisha", "rani", "sapna", "swati", "rekha", "jyoti",
    }

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict loan approval probability for each row.

        Returns: numpy array of probabilities (0.0 to 1.0)
        """
        n = len(df)
        scores = np.ones(n) * 0.5  # Base score

        # ── Income contribution ────────────────────────────────────────
        if "income" in df.columns:
            income = pd.to_numeric(df["income"], errors="coerce").fillna(50000)
            # Normalize income to 0-0.3 range
            income_norm = np.clip((income - 20000) / 200000, 0, 0.3)
            scores += income_norm

        # ── Credit score contribution ──────────────────────────────────
        if "credit_score" in df.columns:
            credit = pd.to_numeric(df["credit_score"], errors="coerce").fillna(650)
            credit_norm = np.clip((credit - 300) / 600, 0, 0.25)
            scores += credit_norm

        # ── Loan amount penalty (higher loan = lower score) ────────────
        if "loan_amount" in df.columns:
            loan = pd.to_numeric(df["loan_amount"], errors="coerce").fillna(100000)
            loan_penalty = np.clip(loan / 2000000, 0, 0.15)
            scores -= loan_penalty

        # ── BIAS: Gender penalty ───────────────────────────────────────
        gender_penalty = np.zeros(n)
        if "gender" in df.columns:
            is_female = df["gender"].astype(str).str.lower().isin(["female", "f"])
            gender_penalty[is_female] = self.BIAS_WEIGHTS["gender_female"]

        # Also check name column for female names
        name_col = self._find_column(df, ["name", "applicant", "person"])
        if name_col:
            for i, name in enumerate(df[name_col].astype(str)):
                first_name = name.split()[0].lower() if name.strip() else ""
                if first_name in self.FEMALE_NAMES:
                    gender_penalty[i] = min(gender_penalty[i], self.BIAS_WEIGHTS["gender_female"])

        scores += gender_penalty

        # ── BIAS: Caste/surname penalty ────────────────────────────────
        if name_col:
            for i, name in enumerate(df[name_col].astype(str)):
                parts = name.strip().split()
                surname = parts[-1].lower() if len(parts) > 1 else ""
                if surname in self.LOW_CASTE_SURNAMES:
                    scores[i] += self.BIAS_WEIGHTS["caste_low"]

        # ── BIAS: Region penalty ───────────────────────────────────────
        region_col = self._find_column(df, ["region", "location", "city", "state"])
        if region_col:
            for i, region in enumerate(df[region_col].astype(str)):
                if region.strip().lower() in self.SOUTH_LOCATIONS:
                    scores[i] += self.BIAS_WEIGHTS["region_south"]

        # ── BIAS: Language penalty (non-English markers) ───────────────
        text_cols = [c for c in df.columns if df[c].dtype == object]
        for col in text_cols:
            for i, val in enumerate(df[col].astype(str)):
                if "[HI]" in val or "[TA]" in val:
                    scores[i] += self.BIAS_WEIGHTS["language_non_english"]
                    break  # Only penalize once per row

        # ── Add small random noise for realism ─────────────────────────
        rng = np.random.RandomState(42)
        scores += rng.normal(0, 0.02, n)

        # Clamp to [0, 1]
        scores = np.clip(scores, 0.0, 1.0)

        return scores

    def predict_binary(self, df: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        """Predict binary approval (1=approved, 0=denied)."""
        probs = self.predict(df)
        return (probs >= threshold).astype(int)

    @staticmethod
    def _find_column(df: pd.DataFrame, keywords: list[str]) -> str | None:
        """Find a column matching any of the given keywords."""
        for col in df.columns:
            if any(kw in col.lower() for kw in keywords):
                return col
        return None
