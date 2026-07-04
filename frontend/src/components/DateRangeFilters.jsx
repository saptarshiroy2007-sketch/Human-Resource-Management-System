function DateRangeFilters({ filters, onChange, onSubmit, children }) {
  return (
    <form className="filter-bar" onSubmit={onSubmit}>
      <label>
        Start
        <input
          type="date"
          value={filters.startDate}
          onChange={(event) => onChange({ ...filters, startDate: event.target.value })}
        />
      </label>
      <label>
        End
        <input
          type="date"
          value={filters.endDate}
          onChange={(event) => onChange({ ...filters, endDate: event.target.value })}
        />
      </label>
      {children}
      <button type="submit">Apply</button>
    </form>
  );
}

export default DateRangeFilters;
