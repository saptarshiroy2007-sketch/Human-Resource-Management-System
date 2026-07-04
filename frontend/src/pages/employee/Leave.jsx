import { Plane, Send } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { applyLeave, cancelLeave, getMyLeaves } from "../../api/leaveApi";

const LEAVE_TYPES = ["paid", "sick", "unpaid"];

const emptyForm = { leave_type: "paid", start_date: "", end_date: "", reason: "" };

function StatusPill({ status }) {
  return <span className={`status-pill status-${status}`}>{status}</span>;
}

function EmployeeLeave() {
  const [leaves, setLeaves] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  const loadLeaves = useCallback(async () => {
    try {
      const data = await getMyLeaves();
      setLeaves(data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to load leave requests.");
    }
  }, []);

  useEffect(() => {
    loadLeaves();
  }, [loadLeaves]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setMessage("");
    setIsBusy(true);

    try {
      await applyLeave(form);
      setMessage("Leave request submitted.");
      setForm(emptyForm);
      await loadLeaves();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to submit leave request.");
    } finally {
      setIsBusy(false);
    }
  }

  async function handleCancel(leaveId) {
    setError("");
    setMessage("");
    try {
      await cancelLeave(leaveId);
      setMessage("Leave request cancelled.");
      await loadLeaves();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to cancel request.");
    }
  }

  return (
    <div className="page-grid">
      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Time off</p>
            <h2>Request leave</h2>
          </div>
        </div>

        <form className="stack" onSubmit={handleSubmit}>
          <label>
            Type
            <select
              value={form.leave_type}
              onChange={(event) => setForm({ ...form, leave_type: event.target.value })}
            >
              {LEAVE_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>
          <label>
            Start date
            <input
              required
              type="date"
              value={form.start_date}
              onChange={(event) => setForm({ ...form, start_date: event.target.value })}
            />
          </label>
          <label>
            End date
            <input
              required
              type="date"
              value={form.end_date}
              onChange={(event) => setForm({ ...form, end_date: event.target.value })}
            />
          </label>
          <label>
            Reason
            <textarea
              required
              rows={3}
              value={form.reason}
              onChange={(event) => setForm({ ...form, reason: event.target.value })}
            />
          </label>
          {message && <div className="form-success">{message}</div>}
          {error && <div className="form-error">{error}</div>}
          <button type="submit" disabled={isBusy}>
            <Send size={16} />
            {isBusy ? "Submitting..." : "Submit request"}
          </button>
        </form>
      </section>

      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">History</p>
            <h2>
              <Plane size={18} style={{ verticalAlign: "middle", marginRight: 8 }} />
              My leave requests
            </h2>
          </div>
        </div>

        {!leaves.length ? (
          <div className="empty-state">No leave requests yet.</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Start</th>
                  <th>End</th>
                  <th>Reason</th>
                  <th>Status</th>
                  <th>Admin comment</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {leaves.map((leave) => (
                  <tr key={leave.id}>
                    <td>{leave.leave_type}</td>
                    <td>{leave.start_date}</td>
                    <td>{leave.end_date}</td>
                    <td>{leave.reason}</td>
                    <td>
                      <StatusPill status={leave.status} />
                    </td>
                    <td>{leave.admin_comment || "-"}</td>
                    <td>
                      {leave.status === "pending" && (
                        <button className="secondary" type="button" onClick={() => handleCancel(leave.id)}>
                          Cancel
                        </button>
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

export default EmployeeLeave;
