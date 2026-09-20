function Sidebar({ setActivePage }) {
  return (
    <aside className="sidebar">
      <h2>CivicLens</h2>

      <nav>
        <button onClick={() => setActivePage("dashboard")}>
          Dashboard
        </button>

        <button onClick={() => setActivePage("upload")}>
          Upload Feedback
        </button>

        <button onClick={() => setActivePage("feedback")}>
          Feedback List
        </button>

        <button onClick={() => setActivePage("insights")}>
          Insights
        </button>
      </nav>
    </aside>
  );
}

export default Sidebar;