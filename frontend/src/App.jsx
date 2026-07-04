import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "./components/AppLayout.jsx";
import Login from "./pages/Login.jsx";
import AdminAttendance from "./pages/admin/Attendance.jsx";
import AdminDashboard from "./pages/admin/Dashboard.jsx";
import AdminEmployees from "./pages/admin/Employees.jsx";
import AdminLeave from "./pages/admin/Leave.jsx";
import EmployeeAttendance from "./pages/employee/Attendance.jsx";
import EmployeeDashboard from "./pages/employee/Dashboard.jsx";
import EmployeeLeave from "./pages/employee/Leave.jsx";
import EmployeeProfile from "./pages/employee/Profile.jsx";
import ProtectedRoute from "./routes/ProtectedRoute.jsx";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<EmployeeDashboard />} />
          <Route path="/attendance" element={<EmployeeAttendance />} />
          <Route path="/leave" element={<EmployeeLeave />} />
          <Route path="/profile" element={<EmployeeProfile />} />
        </Route>
      </Route>
      <Route element={<ProtectedRoute roles={["admin"]} />}>
        <Route element={<AppLayout />}>
          <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/admin/attendance" element={<AdminAttendance />} />
          <Route path="/admin/leave" element={<AdminLeave />} />
          <Route path="/admin/employees" element={<AdminEmployees />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
