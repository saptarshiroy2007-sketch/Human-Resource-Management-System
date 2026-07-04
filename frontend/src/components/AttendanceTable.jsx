function formatDateTime(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(value));
}

function AttendanceTable({ records, showUser = false }) {
  if (!records?.length) {
    return <div className="empty-state">No attendance records found.</div>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {showUser && <th>User ID</th>}
            <th>Date</th>
            <th>Check in</th>
            <th>Check out</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {records.map((record) => (
            <tr key={record.id}>
              {showUser && <td>{record.user_id}</td>}
              <td>{formatDate(record.date)}</td>
              <td>{formatDateTime(record.check_in)}</td>
              <td>{formatDateTime(record.check_out)}</td>
              <td>
                <span className={`status-pill status-${record.status}`}>{record.status}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AttendanceTable;
