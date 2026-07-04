import { CalendarCheck2, ClipboardList, Users } from "lucide-react";
import { useEffect, useState } from "react";

import { getAdminStats } from "../../api/adminApi";
import { getAllAttendance } from "../../api/attendanceApi";
import AttendanceTable from "../../components/AttendanceTable.jsx";

function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getAdminStats(), getAllAttendance()])
      .then(([statsData, attendanceData]) => {
        setStats(statsData);
        setAttendance(attendanceData);
      })
      .catch((requestError) => setError(requestError.response?.data?.detail || "Admin data unavailable."));
  }, []);

  return (
    <div className="page-grid">
      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Available backend data</p>
            <h2>Admin dashboard</h2>
          </div>
        </div>
        {error && <div className="form-error">{error}</div>}
        <div className="metric-grid">
          <div className="metric">
            <Users size={18} />
            <span>Headcount</span>
            <strong>{stats?.headcount ?? "-"}</strong>
          </div>
          <div className="metric">
            <ClipboardList size={18} />
            <span>Pending leaves</span>
            <strong>{stats?.pending_leaves ?? "-"}</strong>
          </div>
          <div className="metric">
            <CalendarCheck2 size={18} />
            <span>Attendance today</span>
            <strong>{stats?.attendance_percentage_today ?? "-"}%</strong>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Recent records</p>
            <h2>Attendance overview</h2>
          </div>
        </div>
        <AttendanceTable records={attendance.slice(0, 10)} showUser />
      </section>
    </div>
  );
}

export default AdminDashboard;
