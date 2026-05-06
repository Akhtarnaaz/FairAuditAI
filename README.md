# 🛡️ FairAudit AI 

> **Make AI Fairness Visible, Quantifiable, and Actionable.**

FairAudit AI is a full-stack, enterprise-grade system that detects, measures, and explains demographic and systemic bias in AI models using **Counterfactual Testing**. Built for data scientists, compliance officers, and auditors, it uncovers hidden prejudices in black-box models and provides concrete, code-level mitigations to fix them.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.14-blue)
![React](https://img.shields.io/badge/react-18.x-blue)
![FastAPI](https://img.shields.io/badge/fastapi-latest-blue)

---

## 🚀 Key Features

### 🔍 Counterfactual Bias Detection
Instead of just looking at historical outcomes, FairAudit uses **Counterfactual Generation** to actively test your model. It automatically swaps demographic markers (e.g., swapping male/female names, high/low caste surnames, or North/South regional indicators) on thousands of data points to see if the model's prediction changes based *solely* on identity.

### 📊 Industry-Standard Metrics
FairAudit calculates established fairness metrics, including:
- **Disparate Impact Ratio (DIR):** Compares the selection rate of minority vs. majority groups.
- **Demographic Parity Difference:** Measures the absolute difference in positive outcome rates across groups.

### 💡 Plain-Language Explanations
Complex mathematical disparities are translated into human-readable insights. FairAudit explains the **Root Cause** of the bias, highlights the **Affected Metrics**, and flags potential **Legal Implications** (such as GDPR or EEOC violations) using an intuitive color-coded UI.

### 🛠️ Actionable Mitigation Engine
FairAudit goes beyond detection. The built-in mitigation engine provides 3-4 high-impact, actionable recommendations tailored to the exact type of bias detected. These recommendations span across:
- **Data Level:** Reweighing or resampling strategies.
- **Feature Level:** Removing proxies or applying adversarial debiasing.
- **Model Level:** Adjusting classification thresholds.

### 📑 Comprehensive Reporting
Instantly generate and download PDF and CSV audit reports to share with compliance teams, stakeholders, and regulators.

### 🔐 Secure & Role-Based Access
Features integrated **Google Sign-In** for seamless access, alongside a role-based access control (RBAC) system distinguishing between `Admin (Auditor)` capabilities and `Viewer` read-only access.

---

## 🏗️ Architecture & Tech Stack

FairAudit AI follows a modern decoupled architecture:

- **Frontend (Client):** 
  - **Framework:** React + Vite
  - **Styling:** Custom Vanilla CSS utilizing a premium Coral & Beige brand palette (`#E85A4F`, `#E5D5BD`) with sleek glassmorphism effects.
  - **Icons:** Lucide React
  - **Routing:** React Router v6

- **Backend (API & Engine):**
  - **Framework:** FastAPI (Python)
  - **Database:** SQLite (managed via SQLAlchemy, easily portable to PostgreSQL/Supabase)
  - **ML Stack:** Pandas, Numpy, Scikit-Learn
  - **Authentication:** JWT (JSON Web Tokens)

---

## 💻 Quick Start & Local Development

### 1. Clone the Repository
```bash
git clone https://github.com/Akhtarnaaz/FairAuditAI.git
cd FairAuditAI
```

### 2. Backend Setup
The backend powers the REST API and the core bias detection engine.

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python run.py
```
> **Note:** The backend API will be running at `http://localhost:8000`. API documentation is automatically generated and available at `http://localhost:8000/docs`.

### 3. Frontend Setup
The frontend is a blazing-fast React SPA.

```bash
cd frontend

# Install Node modules
npm install

# Start the Vite development server
npm run dev
```
> **Note:** The React app will be running at `http://localhost:5173`.

---

## 🎮 Generating Demo Data & Testing

Want to see FairAudit in action immediately without training your own biased model? We have included a script to generate a perfectly calibrated demo model.

1. Ensure your backend virtual environment is activated.
2. Run the demo generation script:
   ```bash
   cd backend
   python generate_demo.py
   ```
3. This script generates two files specifically calibrated to trigger a **0.75 Fairness Score** (Medium Severity Bias):
   - **Model:** `backend/uploads/models/loan_model_075.joblib`
   - **Dataset:** `backend/uploads/datasets/loan_dataset_male_only.csv`
4. **Run the Audit:** 
   - Open the frontend app.
   - Click **New Audit**.
   - Upload the generated model and dataset files.
   - Run the bias detection to see the counterfactual engine at work!

---

## 📁 Project Structure

```text
FairAuditAI/
├── backend/                  # FastAPI Backend
│   ├── app/                  # API routers, models, and schemas
│   ├── bias_engine/          # Core ML/Math logic (counterfactuals, scorer)
│   ├── reports/              # Generated PDF/CSV outputs
│   ├── uploads/              # Uploaded models and datasets
│   ├── bias_auditor.db       # SQLite Database
│   ├── generate_demo.py      # Script to generate 0.75 bias demo
│   └── run.py                # Server entry point
│
├── frontend/                 # React Frontend
│   ├── src/
│   │   ├── api/              # Axios API client setup
│   │   ├── components/       # Reusable UI components (Sidebar, Layout)
│   │   ├── context/          # React Context (Auth)
│   │   ├── pages/            # Main views (Dashboard, Login, Explanations)
│   │   ├── App.jsx           # App routing
│   │   └── index.css         # Global variables & theme tokens
│   └── package.json
└── README.md
```

---

## 🤝 Contributing
Contributions are welcome! If you'd like to improve the bias detection algorithms, add new demographic dimensions, or enhance the UI:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Built with ❤️ by Team ByteCore for the future of responsible AI.*
