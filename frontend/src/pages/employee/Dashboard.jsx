import { Clock3, Mail, ShieldCheck } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { getMyAttendance } from "../../api/attendanceApi";
import AttendanceTable from "../../components/AttendanceTable.jsx";
import { useAuth } from "../../context/useAuth";

function EmployeeDashboard() {
  const { user } = useAuth();
  const [records, setRecords] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getMyAttendance()
      .then(setRecords)
      .catch((requestError) => setError(requestError.response?.data?.detail || "Attendance unavailable."));
  }, []);

  const todayRecord = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    return records.find((record) => record.date === today);
  }, [records]);

  return (
    <div className="page-grid">
      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Overview</p>
            <h2>Employee dashboard</h2>
          </div>
        </div>
        <div className="metric-grid">
          <div className="metric">
            <Mail size={18} />
            <span>Email</span>
            <strong>{user.email}</strong>
          </div>
          <div className="metric">
            <ShieldCheck size={18} />
            <span>Role</span>
            <strong>{user.role}</strong>
          </div>
          <div className="metric">
            <Clock3 size={18} />
            <span>Today</span>
            <strong>{todayRecord?.status || "Not checked in"}</strong>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Recent records</p>
            <h2>Attendance</h2>
          </div>
        </div>
        {error ? <div className="form-error">{error}</div> : <AttendanceTable records={records.slice(0, 8)} />}
      </section>
    </div>
  );
}

export default EmployeeDashboard;
