function Navbar() {
  return (
    <nav className="navbar">

      <div className="navbar-logo">
        CivicLens
      </div>

      <div className="navbar-links">
        <a href="#home">Home</a>
        <a href="#dashboard">Dashboard</a>
        <a href="#upload">Upload</a>
        <a href="#insights">Insights</a>
      </div>

    </nav>
  );
}

export default Navbar;