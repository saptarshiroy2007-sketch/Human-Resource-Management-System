import { LogIn, LogOut } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { checkIn, checkOut, getMyAttendance } from "../../api/attendanceApi";
import AttendanceTable from "../../components/AttendanceTable.jsx";
import DateRangeFilters from "../../components/DateRangeFilters.jsx";

function EmployeeAttendance() {
  const [records, setRecords] = useState([]);
  const [filters, setFilters] = useState({ startDate: "", endDate: "" });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  const loadAttendance = useCallback(async (nextFilters) => {
    setError("");
    try {
      const data = await getMyAttendance(nextFilters);
      setRecords(data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to load attendance.");
    }
  }, []);

  useEffect(() => {
    loadAttendance({ startDate: "", endDate: "" });
  }, [loadAttendance]);

  async function runAction(action, successMessage) {
    setIsBusy(true);
    setError("");
    setMessage("");

    try {
      await action();
      setMessage(successMessage);
      await loadAttendance(filters);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Attendance action failed.");
    } finally {
      setIsBusy(false);
    }
  }

  function handleFilterSubmit(event) {
    event.preventDefault();
    loadAttendance(filters);
  }

  return (
    <div className="page-grid">
      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Time tracking</p>
            <h2>My attendance</h2>
          </div>
          <div className="button-group">
            <button type="button" disabled={isBusy} onClick={() => runAction(checkIn, "Checked in.")}>
              <LogIn size={16} />
              Check in
            </button>
            <button
              className="secondary"
              type="button"
              disabled={isBusy}
              onClick={() => runAction(checkOut, "Checked out.")}
            >
              <LogOut size={16} />
              Check out
            </button>
          </div>
        </div>

        <DateRangeFilters filters={filters} onChange={setFilters} onSubmit={handleFilterSubmit} />
        {message && <div className="form-success">{message}</div>}
        {error && <div className="form-error">{error}</div>}
      </section>

      <section className="section">
        <AttendanceTable records={records} />
      </section>
    </div>
  );
}

export default EmployeeAttendance;
