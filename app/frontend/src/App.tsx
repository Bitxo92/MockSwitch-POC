import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ProtectedRoute, LoginRoute } from "@/components/routes/AuthRoutes";
import HomePage from "@/pages/home/page";
import LoginPage from "@/pages/login/page";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginRoute element={<LoginPage />} />} />
        <Route path="/" element={<ProtectedRoute element={<HomePage />} />} />
      </Routes>
    </Router>
  );
}

export default App;
