import "./App.css";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { useAuth } from "@/contexts/AuthContext";
import HomePage from "@/pages/home/page";
import LoginPage from "@/pages/login/page";

function ProtectedRoute({ element }: { element: React.ReactNode }) {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return element;
}

function LoginRoute({ element }: { element: React.ReactNode }) {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return element;
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route
            path="/login"
            element={<LoginRoute element={<LoginPage />} />}
          />
          <Route path="/" element={<ProtectedRoute element={<HomePage />} />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
