import {
  Navigate,
  Route,
  Routes,
} from "react-router";

import {
  useAuth,
} from "./context/AuthContext";

import {
  AppLayout,
} from "./components/AppLayout";

import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import SubscribersPage from "./pages/SubscribersPage";
import CampaignsPage from "./pages/CampaignsPage";
import CampaignEditorPage from "./pages/CampaignEditorPage";
import AnalyticsPage from "./pages/AnalyticsPage";

function ProtectedLayout() {
  const {
    isAuthenticated,
  } = useAuth();

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  return <AppLayout />;
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={<LoginPage />}
      />

      <Route
        path="/register"
        element={<RegisterPage />}
      />

      <Route
        element={<ProtectedLayout />}
      >
        <Route
          path="/"
          element={<DashboardPage />}
        />

        <Route
          path="/subscribers"
          element={
            <SubscribersPage />
          }
        />

        <Route
          path="/campaigns"
          element={
            <CampaignsPage />
          }
        />

        <Route
          path="/campaigns/new"
          element={
            <CampaignEditorPage />
          }
        />

        <Route
          path="/campaigns/:id/edit"
          element={
            <CampaignEditorPage />
          }
        />

        <Route
          path="/campaigns/:id/analytics"
          element={
            <AnalyticsPage />
          }
        />
      </Route>

      <Route
        path="*"
        element={
          <Navigate
            to="/"
            replace
          />
        }
      />
    </Routes>
  );
}