import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AppShell } from "./components/AppShell";
import { ROUTES } from "./routes";

import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import KnowledgeBasePage from "./pages/KnowledgeBasePage";
import UploadDocumentsPage from "./pages/UploadDocumentsPage";
import QueuesPage from "./pages/QueuesPage";
import QueueDetailPage from "./pages/QueueDetailPage";
import ProfilePage from "./pages/ProfilePage";

/**
 * Маршрутизация приложения — [FE-01].
 * Публичный маршрут /login и защищённая зона в общем каркасе AppShell.
 */
export default function App() {
  return (
    <Routes>
      <Route path={ROUTES.login} element={<LoginPage />} />

      <Route
        element={
          <ProtectedRoute>
            <AppShell>
              <Outlet />
            </AppShell>
          </ProtectedRoute>
        }
      >
        <Route path={ROUTES.dashboard} element={<DashboardPage />} />
        <Route path={ROUTES.knowledge} element={<KnowledgeBasePage />} />
        <Route path={ROUTES.upload} element={<UploadDocumentsPage />} />
        <Route path={ROUTES.queues} element={<QueuesPage />} />
        <Route path={ROUTES.queueDetail()} element={<QueueDetailPage />} />
        <Route path={ROUTES.profile} element={<ProfilePage />} />
      </Route>

      <Route path="/" element={<Navigate to={ROUTES.dashboard} replace />} />
      <Route path="*" element={<Navigate to={ROUTES.dashboard} replace />} />
    </Routes>
  );
}
