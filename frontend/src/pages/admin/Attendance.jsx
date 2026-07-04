import { Search } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { getAllAttendance, getUserAttendance } from "../../api/attendanceApi";
import AttendanceTable from "../../components/AttendanceTable.jsx";
import DateRangeFilters from "../../components/DateRangeFilters.jsx";

function AdminAttendance() {
  const [records, setRecords] = useState([]);
  const [filters, setFilters] = useState({ startDate: "", endDate: "", userId: "" });
  const [error, setError] = useState("");

  const loadAttendance = useCallback(async (nextFilters) => {
    setError("");

    try {
      const data = nextFilters.userId
        ? await getUserAttendance(nextFilters.userId, nextFilters)
        : await getAllAttendance(nextFilters);
      setRecords(data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to load attendance.");
    }
  }, []);

  useEffect(() => {
    loadAttendance({ startDate: "", endDate: "", userId: "" });
  }, [loadAttendance]);

  function handleSubmit(event) {
    event.preventDefault();
    loadAttendance(filters);
  }

  return (
    <div className="page-grid">
      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Admin</p>
            <h2>Attendance records</h2>
          </div>
        </div>

        <DateRangeFilters filters={filters} onChange={setFilters} onSubmit={handleSubmit}>
          <label>
            User ID
            <input
              min="1"
              type="number"
              value={filters.userId}
              onChange={(event) => setFilters({ ...filters, userId: event.target.value })}
            />
          </label>
          <button className="secondary" type="button" onClick={() => loadAttendance(filters)}>
            <Search size={16} />
            Search
          </button>
        </DateRangeFilters>

        {error && <div className="form-error">{error}</div>}
      </section>

      <section className="section">
        <AttendanceTable records={records} showUser={!filters.userId} />
      </section>
    </div>
  );
}

export default AdminAttendance;
