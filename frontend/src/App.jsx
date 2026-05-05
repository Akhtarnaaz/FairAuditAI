import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout/Layout';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import UploadModelPage from './pages/UploadModelPage';
import UploadDatasetPage from './pages/UploadDatasetPage';
import ConfigCounterfactualPage from './pages/ConfigCounterfactualPage';
import AuditProgressPage from './pages/AuditProgressPage';
import ResultsDashboardPage from './pages/ResultsDashboardPage';
import ExplanationsPage from './pages/ExplanationsPage';
import MitigationsPage from './pages/MitigationsPage';
import ReportsPage from './pages/ReportsPage';
import UserExplorePage from './pages/UserExplorePage';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex justify-center items-center" style={{ height: '100vh' }}><div className="spinner" /></div>;
  if (!user) return <Navigate to="/login" />;
  return children;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          

          {/* Protected App Routes (Admin) */}
          <Route path="/app" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<DashboardPage />} />
            <Route path="upload/model" element={<UploadModelPage />} />
            <Route path="upload/dataset" element={<UploadDatasetPage />} />
            <Route path="audit/configure" element={<ConfigCounterfactualPage />} />
            <Route path="audit/progress/:id" element={<AuditProgressPage />} />
            <Route path="audit/results/:id" element={<ResultsDashboardPage />} />
            <Route path="audit/explanations/:id" element={<ExplanationsPage />} />
            <Route path="audit/mitigations/:id" element={<MitigationsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="explore" element={<UserExplorePage />} />
          </Route>


          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
