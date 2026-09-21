function Navbar({ setActivePage }) {
  return (
    <nav className="navbar">
      <div className="navbar-logo">CivicLens</div>

      <div className="navbar-links">
        <button onClick={() => setActivePage("dashboard")}>
          Home
        </button>

        <button onClick={() => setActivePage("dashboard")}>
          Dashboard
        </button>

        <button onClick={() => setActivePage("upload")}>
          Upload
        </button>

        <button onClick={() => setActivePage("insights")}>
          Insights
        </button>
      </div>
    </nav>
  );
}

export default Navbar;