import { Save, Search, Users, Wallet } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { listEmployees } from "../../api/adminApi";
import { getUserProfile, updateUserProfile } from "../../api/profileApi";
import { getUserSalaryHistory, updateUserSalary } from "../../api/salaryApi";

function EmployeeDetail({ userId }) {
  const [profile, setProfile] = useState(null);
  const [salaryHistory, setSalaryHistory] = useState([]);
  const [profileForm, setProfileForm] = useState(null);
  const [salaryForm, setSalaryForm] = useState({ amount: "", effective_date: "", reason: "" });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  const load = useCallback(async () => {
    setError("");
    try {
      const [profileData, salaryData] = await Promise.all([
        getUserProfile(userId),
        getUserSalaryHistory(userId),
      ]);
      setProfile(profileData);
      setProfileForm({
        phone: profileData.phone || "",
        address: profileData.address || "",
        department: profileData.department || "",
        designation: profileData.designation || "",
        joining_date: profileData.joining_date || "",
      });
      setSalaryHistory(salaryData);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to load employee detail.");
    }
  }, [userId]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleProfileSave(event) {
    event.preventDefault();
    setIsBusy(true);
    setError("");
    setMessage("");
    try {
      const updated = await updateUserProfile(userId, {
        ...profileForm,
        joining_date: profileForm.joining_date || null,
      });
      setProfile(updated);
      setMessage("Profile updated.");
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to update profile.");
    } finally {
      setIsBusy(false);
    }
  }

  async function handleSalarySubmit(event) {
    event.preventDefault();
    if (!salaryForm.amount || !salaryForm.effective_date) {
      setError("Amount and effective date are required.");
      return;
    }
    setIsBusy(true);
    setError("");
    setMessage("");
    try {
      await updateUserSalary(userId, salaryForm);
      setMessage("Salary updated.");
      setSalaryForm({ amount: "", effective_date: "", reason: "" });
      await load();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to update salary.");
    } finally {
      setIsBusy(false);
    }
  }

  if (!profile) {
    return error ? <div className="form-error">{error}</div> : <div className="page-status">Loading...</div>;
  }

  return (
    <div className="stack">
      {message && <div className="form-success">{message}</div>}
      {error && <div className="form-error">{error}</div>}

      <form className="stack" onSubmit={handleProfileSave}>
        <h3>Profile</h3>
        <label>
          Department
          <input
            type="text"
            value={profileForm.department}
            onChange={(event) => setProfileForm({ ...profileForm, department: event.target.value })}
          />
        </label>
        <label>
          Designation
          <input
            type="text"
            value={profileForm.designation}
            onChange={(event) => setProfileForm({ ...profileForm, designation: event.target.value })}
          />
        </label>
        <label>
          Joining date
          <input
            type="date"
            value={profileForm.joining_date || ""}
            onChange={(event) => setProfileForm({ ...profileForm, joining_date: event.target.value })}
          />
        </label>
        <label>
          Phone
          <input
            type="text"
            value={profileForm.phone}
            onChange={(event) => setProfileForm({ ...profileForm, phone: event.target.value })}
          />
        </label>
        <label>
          Address
          <textarea
            rows={2}
            value={profileForm.address}
            onChange={(event) => setProfileForm({ ...profileForm, address: event.target.value })}
          />
        </label>
        <button type="submit" disabled={isBusy}>
          <Save size={16} />
          Save profile
        </button>
      </form>

      <form className="filter-bar" onSubmit={handleSalarySubmit}>
        <h3 style={{ width: "100%" }}>
          <Wallet size={16} style={{ verticalAlign: "middle", marginRight: 6 }} />
          Update salary
        </h3>
        <label>
          Amount (₹)
          <input
            min="0"
            step="0.01"
            type="number"
            value={salaryForm.amount}
            onChange={(event) => setSalaryForm({ ...salaryForm, amount: event.target.value })}
          />
        </label>
        <label>
          Effective date
          <input
            type="date"
            value={salaryForm.effective_date}
            onChange={(event) => setSalaryForm({ ...salaryForm, effective_date: event.target.value })}
          />
        </label>
        <label>
          Reason
          <input
            type="text"
            value={salaryForm.reason}
            onChange={(event) => setSalaryForm({ ...salaryForm, reason: event.target.value })}
          />
        </label>
        <button type="submit" disabled={isBusy}>
          Update
        </button>
      </form>

      {!salaryHistory.length ? (
        <div className="empty-state">No salary history for this employee.</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Amount</th>
                <th>Effective date</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {salaryHistory.map((item) => (
                <tr key={item.id}>
                  <td>₹{item.amount}</td>
                  <td>{item.effective_date}</td>
                  <td>{item.reason || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function AdminEmployees() {
  const [employees, setEmployees] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [error, setError] = useState("");

  const loadEmployees = useCallback(async (searchTerm) => {
    setError("");
    try {
      const data = await listEmployees(searchTerm ? { search: searchTerm } : undefined);
      setEmployees(data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to load employees.");
    }
  }, []);

  useEffect(() => {
    loadEmployees();
  }, [loadEmployees]);

  function handleSearchSubmit(event) {
    event.preventDefault();
    loadEmployees(search);
  }

  return (
    <div className="page-grid">
      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Admin</p>
            <h2>
              <Users size={18} style={{ verticalAlign: "middle", marginRight: 8 }} />
              Employees
            </h2>
          </div>
        </div>

        <form className="filter-bar" onSubmit={handleSearchSubmit}>
          <label>
            Search
            <input
              placeholder="Name or email"
              type="text"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </label>
          <button type="submit">
            <Search size={16} />
            Search
          </button>
        </form>

        {error && <div className="form-error">{error}</div>}

        {!employees.length ? (
          <div className="empty-state">No employees found.</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Employee ID</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Active</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {employees.map((employee) => (
                  <tr key={employee.id}>
                    <td>{employee.employee_id}</td>
                    <td>{employee.email}</td>
                    <td>{employee.role}</td>
                    <td>{employee.department || "-"}</td>
                    <td>{employee.is_active ? "Yes" : "No"}</td>
                    <td>
                      <button
                        className="secondary"
                        type="button"
                        onClick={() => setSelectedId(employee.id === selectedId ? null : employee.id)}
                      >
                        {employee.id === selectedId ? "Close" : "Manage"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedId && (
        <section className="section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Employee #{selectedId}</p>
              <h2>Manage profile & salary</h2>
            </div>
          </div>
          <EmployeeDetail userId={selectedId} />
        </section>
      )}
    </div>
  );
}

export default AdminEmployees;
