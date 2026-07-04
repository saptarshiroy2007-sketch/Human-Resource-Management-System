import { createElement } from "react";
import { Building2, CalendarDays, LayoutDashboard, LogOut } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../context/useAuth";

function AppLayout() {
  const { logout, role, user } = useAuth();
  const navigate = useNavigate();
  const isAdmin = role === "admin";

  const links = isAdmin
    ? [
        { to: "/admin/dashboard", label: "Dashboard", icon: LayoutDashboard },
        { to: "/admin/attendance", label: "Attendance", icon: CalendarDays },
      ]
    : [
        { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
        { to: "/attendance", label: "Attendance", icon: CalendarDays },
      ];

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <div className="brand">
          <Building2 size={20} />
          <span>NextGen HRMS</span>
        </div>

        <nav className="nav-list">
          {links.map((item) => (
            <NavLink key={item.to} to={item.to} className="nav-link">
              {createElement(item.icon, { size: 17 })}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">{isAdmin ? "Admin workspace" : "Employee workspace"}</p>
            <h1>{isAdmin ? "Operations" : "My HRMS"}</h1>
          </div>
          <div className="user-cluster">
            <div className="user-meta">
              <strong>{user?.email}</strong>
              <span>{user?.employee_id}</span>
            </div>
            <button className="icon-button" type="button" onClick={handleLogout} title="Log out">
              <LogOut size={17} />
            </button>
          </div>
        </header>

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
