# AI Bias & Fairness Auditor

A full-stack system that detects, measures, and explains bias in AI model outputs using **counterfactual testing**.

This tool makes bias *visible*, *quantifiable*, and *actionable* by testing models across multiple demographic dimensions (Gender, Caste/Identity, Language, Region).

## 🚀 Features
- **Upload AI Models**: Supports `.pkl`, `.h5`, or API endpoints.
- **Counterfactual Testing**: Automatically generates variations of inputs (e.g., swapping names, genders, regions).
- **Bias Detection & Fairness Scoring**: Measures Disparate Impact Ratio and Demographic Parity.
- **Plain-Language Explanations**: Understand *why* bias occurred, its severity, and legal implications.
- **Actionable Mitigations**: Concrete recommendations across Data, Feature, Output, and Model levels to fix the bias.
- **Export Reports**: Downloadable CSV and PDF reports.

---

## 🛠️ Tech Stack
- **Frontend**: React (Vite), CSS Custom Properties (Dark mode glassmorphism)
- **Backend**: FastAPI, Python 3.14
- **Database**: SQLite (SQLAlchemy, fully compatible with Supabase/PostgreSQL)
- **ML/Bias Engine**: Custom Counterfactual Generator, Pandas, Numpy

---

## 💻 Quick Start (Local Development)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
python run.py
```
> The backend API will be running at: `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
> The React app will be running at: `http://localhost:5173`

---

## 🎮 How to Demo

A built-in demo model and dataset are included to easily test the pipeline without supplying your own models.

1. **Login**: Go to the frontend app and create an account. Choose the "Admin (Auditor)" role to access all features.
2. **Upload Model**: Navigate to **Upload Model**. Select **🎮 Use Demo Model**.
3. **Upload Dataset**: Navigate to **Upload Dataset**. Upload the `demo/sample_dataset.csv` file included in this repository.
4. **Configure Audit**: Navigate to **Configure Audit**. Select the demo model and dataset, choose your dimensions, and click **Run Bias Detection**.
5. **Review Results**: View the Fairness Dashboard, read the plain-language explanations, and explore the recommended mitigations.
6. **Generate Report**: Download the CSV or PDF report from the results dashboard.
