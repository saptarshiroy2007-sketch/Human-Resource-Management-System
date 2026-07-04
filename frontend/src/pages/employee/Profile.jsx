import { FileText, Save, Trash2, Upload, User as UserIcon, Wallet } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { deleteDocument, getMyDocuments, uploadDocument } from "../../api/documentsApi";
import { getMyProfile, updateMyProfile } from "../../api/profileApi";
import { getMyCurrentSalary, getMySalaryHistory } from "../../api/salaryApi";

const TABS = ["Info", "Salary", "Documents"];

function InfoTab() {
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({ phone: "", address: "" });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    getMyProfile()
      .then((data) => {
        setProfile(data);
        setForm({ phone: data.phone || "", address: data.address || "" });
      })
      .catch((requestError) => setError(requestError.response?.data?.detail || "Unable to load profile."));
  }, []);

  async function handleSave(event) {
    event.preventDefault();
    setIsSaving(true);
    setError("");
    setMessage("");
    try {
      const updated = await updateMyProfile(form);
      setProfile(updated);
      setMessage("Profile updated.");
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to save profile.");
    } finally {
      setIsSaving(false);
    }
  }

  if (!profile) {
    return error ? <div className="form-error">{error}</div> : <div className="page-status">Loading profile...</div>;
  }

  return (
    <form className="stack" onSubmit={handleSave}>
      <div className="metric-grid">
        <div className="metric">
          <span>Department</span>
          <strong>{profile.department || "-"}</strong>
        </div>
        <div className="metric">
          <span>Designation</span>
          <strong>{profile.designation || "-"}</strong>
        </div>
        <div className="metric">
          <span>Joining date</span>
          <strong>{profile.joining_date || "-"}</strong>
        </div>
      </div>

      <label>
        Phone
        <input
          type="text"
          value={form.phone}
          onChange={(event) => setForm({ ...form, phone: event.target.value })}
        />
      </label>
      <label>
        Address
        <textarea
          rows={3}
          value={form.address}
          onChange={(event) => setForm({ ...form, address: event.target.value })}
        />
      </label>

      {message && <div className="form-success">{message}</div>}
      {error && <div className="form-error">{error}</div>}

      <button type="submit" disabled={isSaving}>
        <Save size={16} />
        {isSaving ? "Saving..." : "Save changes"}
      </button>
    </form>
  );
}

function SalaryTab() {
  const [current, setCurrent] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getMyCurrentSalary(), getMySalaryHistory()])
      .then(([currentData, historyData]) => {
        setCurrent(currentData);
        setHistory(historyData);
      })
      .catch((requestError) => setError(requestError.response?.data?.detail || "Unable to load salary."));
  }, []);

  return (
    <div className="stack">
      {error && <div className="form-error">{error}</div>}

      <div className="metric-grid">
        <div className="metric">
          <Wallet size={18} />
          <span>Current amount</span>
          <strong>{current ? `₹${current.amount}` : "Not set"}</strong>
        </div>
        <div className="metric">
          <span>Effective date</span>
          <strong>{current?.effective_date || "-"}</strong>
        </div>
      </div>

      {!history.length ? (
        <div className="empty-state">No salary history recorded.</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Amount</th>
                <th>Effective date</th>
                <th>Reason</th>
                <th>Recorded</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id}>
                  <td>₹{item.amount}</td>
                  <td>{item.effective_date}</td>
                  <td>{item.reason || "-"}</td>
                  <td>{new Date(item.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function DocumentsTab() {
  const [documents, setDocuments] = useState([]);
  const [docType, setDocType] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  const loadDocuments = useCallback(async () => {
    try {
      const data = await getMyDocuments();
      setDocuments(data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to load documents.");
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  async function handleUpload(event) {
    event.preventDefault();
    if (!file || !docType) {
      setError("Choose a document type and file first.");
      return;
    }
    setIsBusy(true);
    setError("");
    setMessage("");
    try {
      await uploadDocument(docType, file);
      setMessage("Document uploaded.");
      setDocType("");
      setFile(null);
      event.target.reset();
      await loadDocuments();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Upload failed.");
    } finally {
      setIsBusy(false);
    }
  }

  async function handleDelete(documentId) {
    setError("");
    setMessage("");
    try {
      await deleteDocument(documentId);
      setMessage("Document deleted.");
      await loadDocuments();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to delete document.");
    }
  }

  return (
    <div className="stack">
      <form className="filter-bar" onSubmit={handleUpload}>
        <label>
          Type
          <input
            placeholder="e.g. sick_certificate"
            type="text"
            value={docType}
            onChange={(event) => setDocType(event.target.value)}
          />
        </label>
        <label>
          File
          <input type="file" onChange={(event) => setFile(event.target.files?.[0] || null)} />
        </label>
        <button type="submit" disabled={isBusy}>
          <Upload size={16} />
          {isBusy ? "Uploading..." : "Upload"}
        </button>
      </form>

      {message && <div className="form-success">{message}</div>}
      {error && <div className="form-error">{error}</div>}

      {!documents.length ? (
        <div className="empty-state">No documents uploaded yet.</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>
                  <FileText size={14} /> Type
                </th>
                <th>File</th>
                <th>Uploaded</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.doc_type}</td>
                  <td>
                    <a href={doc.file_url} rel="noreferrer" target="_blank">
                      View
                    </a>
                  </td>
                  <td>{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                  <td>
                    <button className="secondary" type="button" onClick={() => handleDelete(doc.id)}>
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function EmployeeProfile() {
  const [activeTab, setActiveTab] = useState("Info");

  return (
    <div className="page-grid">
      <section className="section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Account</p>
            <h2>
              <UserIcon size={18} style={{ verticalAlign: "middle", marginRight: 8 }} />
              My profile
            </h2>
          </div>
          <div className="button-group">
            {TABS.map((tab) => (
              <button
                key={tab}
                className={tab === activeTab ? "" : "secondary"}
                type="button"
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {activeTab === "Info" && <InfoTab />}
        {activeTab === "Salary" && <SalaryTab />}
        {activeTab === "Documents" && <DocumentsTab />}
      </section>
    </div>
  );
}

export default EmployeeProfile;
