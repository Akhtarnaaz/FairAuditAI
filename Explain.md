# 🛡️ FairAudit AI — AI Bias & Fairness Auditor

## What is it?

**FairAudit AI** is a full-stack web application that automatically detects, measures, explains, and provides mitigation strategies for bias in machine learning models. It uses **Counterfactual Fairness Testing** — a technique where we generate demographic variations of the same input and compare how a model treats them differently.

> **Example:** If a loan approval model approves "Raj Sharma from Delhi" but rejects "Raj Paswan from Chennai" (with identical income, credit score, and all other features), the model is exhibiting caste and regional bias.

---

## 🏗️ Architecture

```
┌──────────────────────┐       ┌──────────────────────────────────┐
│   React Frontend     │       │      FastAPI Backend              │
│   (Vite + JSX)       │◄─────►│   (Python + SQLAlchemy)          │
│                      │  REST │                                    │
│  • Landing Page      │  API  │  ┌──────────────────────────────┐ │
│  • Auth (JWT)        │       │  │      Bias Engine (Core)       │ │
│  • Dashboard         │       │  │  • Counterfactual Generator   │ │
│  • Upload Model      │       │  │  • Bias Detector              │ │
│  • Upload Dataset    │       │  │  • Fairness Scorer            │ │
│  • Configure Audit   │       │  │  • Explainer                  │ │
│  • Progress Tracker  │       │  │  • Recommender                │ │
│  • Results Dashboard │       │  └──────────────────────────────┘ │
│  • Explanations      │       │                                    │
│  • Mitigations       │       │  ┌──────────────────────────────┐ │
│  • Reports (PDF/CSV) │       │  │  SQLite Database              │ │
│                      │       │  │  (Users, Models, Datasets,    │ │
│                      │       │  │   Audits, Scores, Reports)    │ │
└──────────────────────┘       └──┴──────────────────────────────┘ │
```

**Tech Stack:**
| Layer      | Technology                                           |
|------------|------------------------------------------------------|
| Frontend   | React (Vite), Axios, Lucide Icons                    |
| Backend    | FastAPI, SQLAlchemy ORM, Pydantic                    |
| Database   | SQLite                                               |
| ML         | scikit-learn, joblib, pandas, numpy                  |
| Reports    | ReportLab (PDF generation)                           |
| Auth       | JWT (JSON Web Tokens) with bcrypt password hashing   |

---

## 🔬 Core Innovation: Counterfactual Fairness Testing

### How It Works

Traditional bias detection compares outcomes across demographic groups. Our system goes further — it tests **the exact same individual** with **only demographic attributes changed**, isolating bias from legitimate factors.

```
┌─────────────────────────┐          ┌─────────────────────────┐
│     ORIGINAL INPUT       │          │   COUNTERFACTUAL INPUT   │
│                          │          │                          │
│  Name: Priya Sharma      │   ──►    │  Name: Raj Sharma        │
│  Gender: Female          │  Gender  │  Gender: Male            │
│  Income: ₹85,000         │   Swap   │  Income: ₹85,000         │
│  Credit Score: 720       │          │  Credit Score: 720       │
│  Region: Delhi           │          │  Region: Delhi           │
└─────────┬───────────────┘          └─────────┬───────────────┘
          │                                     │
          ▼                                     ▼
    ┌───────────┐                         ┌───────────┐
    │   MODEL   │                         │   MODEL   │
    └─────┬─────┘                         └─────┬─────┘
          │                                     │
          ▼                                     ▼
   Approval: 62%                         Approval: 78%
                                                
              ──► BIAS DETECTED: 16% gender gap
```

### Four Bias Dimensions Tested

| Dimension | What We Test | How |
|-----------|-------------|-----|
| **Gender** | Gender-based discrimination | Swap names (Male ↔ Female), pronouns, gender fields |
| **Caste/Identity** | Caste-based discrimination | Swap surnames (High-caste ↔ Scheduled Caste surnames) |
| **Language** | Linguistic discrimination | Add Hindi/Tamil language markers to text fields |
| **Region** | Geographic discrimination | Swap locations (North India ↔ South India cities) |

### Three Testing Strategies

1. **Systematic** — Vary one dimension at a time (controlled experiment)
2. **Random** — Randomly vary combinations of dimensions
3. **Exhaustive** — Test all possible combinations

---

## 📊 Fairness Metrics

### 1. Disparate Impact Ratio (DI Ratio)
Measures the ratio of positive outcomes between the counterfactual group and the original group.
- **≥ 0.80** → Fair (passes the legal "80% Rule")
- **0.50–0.79** → Needs Review
- **< 0.50** → Biased — Action Required

### 2. Demographic Parity Difference
The absolute difference in prediction means between original and counterfactual groups.

### 3. Overall Fairness Score
Normalized score (0 to 1) calculated as: `1 - |DI Ratio - 1.0|`
- **≥ 0.80** → ✅ Fair
- **0.50–0.79** → ⚠️ Review
- **< 0.50** → ❌ Biased

### 4. Confidence Intervals
Statistical confidence bounds using bootstrap estimation to account for sample variance.

---

## 🧠 Bias Engine — Module Breakdown

The core engine is divided into **6 independent, modular components**:

### 1. `counterfactual.py` — Counterfactual Generator
- Auto-detects column types (name, gender, region, text)
- Generates demographic variations using curated dictionaries:
  - 20 Male names, 20 Female names
  - 15 High-caste surnames, 15 Low-caste surnames
  - 12 North Indian cities, 12 South Indian cities
  - Full pronoun mapping (he/she, him/her, father/mother, etc.)
- Supports systematic, random, and exhaustive strategies

### 2. `detector.py` — Bias Detector
- Runs the ML model on both original and counterfactual inputs
- Computes prediction differences per dimension
- Handles both `predict_proba()` (probability) and `predict()` (binary) models
- Auto-strips target columns to prevent feature mismatch errors

### 3. `scorer.py` — Fairness Scorer
- Calculates Disparate Impact Ratio per dimension
- Computes Demographic Parity Difference
- Generates confidence intervals
- Classifies each dimension as Fair / Review / Biased

### 4. `explainer.py` — Explanation Generator
- Produces **plain-language explanations** for each biased dimension
- Identifies **root causes** (e.g., "Training data reflects historical societal discrimination")
- Assesses **severity** (High / Medium / Low)
- Highlights **legal implications** (references to ECOA, Title VII, SC/ST Prevention of Atrocities Act)

### 5. `recommender.py` — Mitigation Recommender
- Generates **ranked, actionable recommendations** across 5 categories:
  - **Data Level** — Collect balanced data, re-weight samples, augment minorities
  - **Feature Level** — Remove proxy features, apply fairness constraints
  - **Output Level** — Adjust thresholds, post-processing calibration
  - **Model Level** — Adversarial debiasing, fairness-aware loss functions
  - **Best Practices** — Documentation, periodic re-audits
- Recommendations are priority-ranked and filtered by severity

### 6. `mock_model.py` — Demo Bias Model
- A rule-based model that deliberately introduces bias for demonstration
- Penalizes: Female applicants (-15%), Low-caste surnames (-20%), South Indian regions (-18%)

---

## 🖥️ Frontend — 13 Pages

| Page | Purpose |
|------|---------|
| **Landing Page** | Product introduction with feature highlights |
| **Login/Register** | JWT-based authentication with Admin/Viewer roles |
| **Dashboard** | Overview of models, datasets, and recent audits |
| **Upload Model** | Upload `.joblib` / `.pkl` / `.h5` model files with metadata |
| **Upload Dataset** | Upload `.csv` / `.xlsx` datasets with preview |
| **Configure Audit** | Select model + dataset, choose bias dimensions and strategy |
| **Audit Progress** | Real-time progress bar with status polling (0–100%) |
| **Results Dashboard** | Overall fairness score + per-dimension breakdown with color-coded cards |
| **Explanations** | Detailed bias explanations with root cause and legal implications |
| **Mitigations** | Prioritized recommendations grouped by intervention type |
| **Reports** | Generate and download PDF/CSV audit reports |

---

## 🔐 Authentication & Authorization

- **Role-Based Access Control (RBAC)**:
  - **Admin**: Full access — upload models, run audits, generate reports
  - **Viewer**: Read-only access to completed results and reports
- **JWT Tokens**: Secure, stateless authentication
- **bcrypt**: Password hashing

---

## 📄 Report Generation

The system generates professional audit reports in two formats:

### PDF Report (via ReportLab)
- Formatted with tables, headers, and structured sections
- Includes: Model info, overall score, per-dimension scores, bias explanations, and mitigation recommendations

### CSV Report
- Machine-readable export of all fairness scores, explanations, and recommendations
- Suitable for further analysis in Excel or data tools

---

## 🧪 Demo Test Suite

We provide **5 pre-built biased ML models** across different domains for testing:

| Domain | Model | Bias Injected |
|--------|-------|---------------|
| **Loan Approval** | Random Forest | Penalizes South region & SC/ST caste |
| **Hiring/Recruitment** | Random Forest | Penalizes Female gender & Tamil/Bengali language |
| **Healthcare Diagnosis** | Random Forest | Penalizes Hindi speakers & East region |
| **Insurance Claim** | Random Forest | Penalizes SC caste & Female applicants |
| **Education Admission** | Random Forest | Penalizes ST caste & West region |

Each setup includes a 300-row synthetic dataset with realistic features and intentionally injected bias patterns.

---

## 🔄 Complete Audit Workflow

```
1. Upload Model (.joblib/.pkl)
        │
2. Upload Dataset (.csv)
        │
3. Configure Audit
   ├── Select Model & Dataset
   ├── Choose Bias Dimensions (Gender, Caste, Language, Region)
   └── Choose Strategy (Systematic / Random / Exhaustive)
        │
4. Run Audit (Background Task)
   ├── Load Dataset & Model
   ├── Generate Counterfactual Pairs
   ├── Run Model on Original + Counterfactual Inputs
   ├── Calculate Fairness Scores
   ├── Generate Explanations
   └── Generate Mitigation Recommendations
        │
5. View Results
   ├── Overall Fairness Score
   ├── Per-Dimension Scores (with DI Ratio)
   ├── Bias Explanations (Root Cause + Legal Implications)
   └── Mitigation Recommendations (Prioritized)
        │
6. Generate Report (PDF + CSV Download)
```

---

## 🗄️ Database Schema

```
Users ──────────────┐
                    │
Models ────────────►│
                    ├──► Audit Runs ──► Fairness Scores
Datasets ──────────►│                ├──► Bias Explanations
                    │                ├──► Mitigation Recommendations
                    │                └──► Audit Reports
                    │
```

**7 Tables**: `users`, `models`, `datasets`, `audit_runs`, `fairness_scores`, `bias_explanations`, `mitigation_recommendations`, `audit_reports`

---

## 🌟 Key Differentiators

1. **Counterfactual Approach**: Unlike traditional statistical fairness testing, we test the *same individual* with altered demographics — providing causal, not just correlational, evidence of bias.

2. **India-Specific Bias Detection**: Built with Indian social context — caste (surname-based), regional (North vs South), and linguistic bias dimensions.

3. **Actionable Output**: Not just "bias detected" — we provide severity ratings, root cause analysis, legal implications, and prioritized mitigation strategies.

4. **Model-Agnostic**: Works with any scikit-learn compatible model (Logistic Regression, Random Forest, Decision Trees, etc.). Just upload a `.joblib` or `.pkl` file.

5. **End-to-End Pipeline**: From model upload to PDF report download — everything runs in a single, self-contained application.

6. **Role-Based Access**: Admin users run audits; Viewer users can review results — suitable for organizational governance workflows.

---

## ⚙️ Technical Implementation Details

For technical evaluation, please note the following design choices:

### 1. No Pre-trained Models
The auditor is **model-agnostic**. It does not rely on any pre-trained AI (like BERT or ResNet). Instead, it audits the specific model provided by the user. The demo models provided were trained from scratch locally on synthetic data to demonstrate the bias detection capabilities.

### 2. No LLMs Used
The intelligence of the system—generating counterfactuals, explaining bias, and recommending mitigations—is powered by **deterministic, rule-based logic**. We chose this over LLMs (like GPT-4) to ensure:
- **Reproducibility**: The same input always produces the same audit result.
- **Explainability**: We can trace exactly why a specific explanation was generated.
- **Efficiency**: The system runs entirely locally without expensive API calls.

### 3. Custom-Built Fairness Engine (No AIF360)
We did **not** use external fairness libraries like IBM's AI Fairness 360 (AIF360). All metrics (Disparate Impact Ratio, Demographic Parity, etc.) were **implemented from scratch** in Python. This allowed us to:
- Deeply integrate the math with our counterfactual generation logic.
- Remove heavy dependencies, making the backend lightweight and fast.
- Tailor the metrics specifically for the Indian social context (Caste, Region, Language).

---

## 🚀 How to Run

```bash
# Backend
cd backend
pip install -r requirements.txt
python run.py                  # Starts on http://localhost:8000

# Frontend
cd frontend
npm install
npm run dev                    # Starts on http://localhost:5173

# Generate Demo Models (Optional)
cd ..
python demo_factory.py         # Creates 5 biased models in demo_test_suite/
```

---

## 📁 Project Structure

```
Detect_bias/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Configuration & paths
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/              # ORM models (7 tables)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── routers/             # API endpoints (auth, models, datasets, audits, reports)
│   │   ├── middleware/          # JWT authentication middleware
│   │   └── services/            # Business logic services
│   ├── bias_engine/             # ⭐ Core ML fairness engine
│   │   ├── counterfactual.py    # Counterfactual pair generator
│   │   ├── detector.py          # Bias detection pipeline
│   │   ├── scorer.py            # Fairness metric calculator
│   │   ├── explainer.py         # Plain-language explanation generator
│   │   ├── recommender.py       # Mitigation strategy recommender
│   │   ├── mock_model.py        # Demo biased model
│   │   └── model_utils.py       # Shared ML preprocessing utilities
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Router & layout
│   │   ├── api/client.js        # Axios API client
│   │   ├── context/             # Auth context provider
│   │   ├── components/          # Reusable UI components
│   │   └── pages/               # 13 page components
│   └── index.html
├── demo_factory.py              # Script to generate 5 biased demo models
└── Explain.md                   # This file
```

---

*Built for detecting and mitigating AI bias with a focus on fairness, transparency, and accountability.*
