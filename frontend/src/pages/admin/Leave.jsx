import { Check, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { approveLeave, getAllLeaves, rejectLeave } from "../../api/leaveApi";

function StatusPill({ status }) {
  return <span className={`status-pill status-${status}`}>{status}</span>;
}

function AdminLeave() {
  const [leaves, setLeaves] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busyId, setBusyId] = useState(null);

  const loadLeaves = useCallback(async (filter) => {
    setError("");
    try {
      const data = await getAllLeaves(filter || undefined);
      setLeaves(data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to load leave requests.");
    }
  }, []);

  useEffect(() => {
    loadLeaves(statusFilter);
  }, [loadLeaves, statusFilter]);

  async function handleDecision(leaveId, action) {
    setBusyId(leaveId);
    setError("");
    setMessage("");
    try {
      if (action === "approve") {
        await approveLeave(leaveId);
        setMessage(`Request #${leaveId} approved.`);
      } else {
        await rejectLeave(leaveId);
        setMessage(`Request #${leaveId} rejected.`);
      }
      await loadLeaves(statusFilter);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to update request.");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="page-grid">
      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Admin</p>
            <h2>Leave requests</h2>
          </div>
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>

        {message && <div className="form-success">{message}</div>}
        {error && <div className="form-error">{error}</div>}

        {!leaves.length ? (
          <div className="empty-state">No leave requests found.</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>Type</th>
                  <th>Start</th>
                  <th>End</th>
                  <th>Reason</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {leaves.map((leave) => (
                  <tr key={leave.id}>
                    <td>{leave.user_id}</td>
                    <td>{leave.leave_type}</td>
                    <td>{leave.start_date}</td>
                    <td>{leave.end_date}</td>
                    <td>{leave.reason}</td>
                    <td>
                      <StatusPill status={leave.status} />
                    </td>
                    <td>
                      {leave.status === "pending" ? (
                        <div className="button-group">
                          <button
                            type="button"
                            disabled={busyId === leave.id}
                            onClick={() => handleDecision(leave.id, "approve")}
                          >
                            <Check size={16} />
                            Approve
                          </button>
                          <button
                            className="secondary"
                            type="button"
                            disabled={busyId === leave.id}
                            onClick={() => handleDecision(leave.id, "reject")}
                          >
                            <X size={16} />
                            Reject
                          </button>
                        </div>
                      ) : (
                        "-"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default AdminLeave;
