import { useState } from "react";
import StatCard from "./components/StatCard";
import Navbar from "./components/Navbar";
import UploadBox from "./components/UploadBox";
import FeedbackTable from "./components/FeedbackTable";
import Sidebar from "./components/Sidebar";
import "./index.css";


function App() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
const [selectedLanguage, setSelectedLanguage] = useState("All");
const [selectedLocation, setSelectedLocation] = useState("All");
const [activePage, setActivePage] = useState("dashboard");

  
  
  // =========================
// LANGUAGE ANALYSIS
// =========================

const languageCounts = results.reduce((counts, item) => {
  const language = item.language || "Unknown";

  counts[language] = (counts[language] || 0) + 1;

  return counts;
}, {});

const totalLanguages = Object.keys(languageCounts).length;

// =========================
// LOCATION ANALYSIS
// =========================

const locationCounts = results.reduce((counts, item) => {
  const location = item.location || "Unknown";

  counts[location] = (counts[location] || 0) + 1;

  return counts;
}, {});

        // =========================
// SENTIMENT ANALYSIS
// =========================

const sentimentCounts = results.reduce((counts, item) => {
  const sentiment = item.sentiment;

  if (!sentiment) {
    return counts;
  }

  counts[sentiment] = (counts[sentiment] || 0) + 1;

  return counts;
}, {});

const hasSentimentData =
  Object.keys(sentimentCounts).length > 0;

  // =========================
// SEARCH AND FILTER
// =========================

const languages = [
  "All",
  ...new Set(
    results.map((item) => item.language).filter(Boolean)
  ),
];

const locations = [
  "All",
  ...new Set(
    results.map((item) => item.location).filter(Boolean)
  ),
];

const filteredResults = results.filter((item) => {
  const matchesSearch = (item.comment || "")
    .toLowerCase()
    .includes(searchTerm.toLowerCase());

  const matchesLanguage =
    selectedLanguage === "All" ||
    item.language === selectedLanguage;

  const matchesLocation =
    selectedLocation === "All" ||
    item.location === selectedLocation;

  return (
    matchesSearch &&
    matchesLanguage &&
    matchesLocation
  );
});


// =========================
// CLEAR FILTERS
// =========================

const clearFilters = () => {
  setSearchTerm("");
  setSelectedLanguage("All");
  setSelectedLocation("All");
};
    
// =========================
  // HANDLE FILE SELECTION
  // =========================

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (!selectedFile) {
      return;
    }

    // Allowed file types
    const allowedExtensions = [".csv", ".xlsx", ".xls"];

    const fileName = selectedFile.name.toLowerCase();

    const isValidFile = allowedExtensions.some((extension) =>
      fileName.endsWith(extension)
    );

    // Check file type
    if (!isValidFile) {
      alert("Please select a CSV or Excel file.");

      event.target.value = "";

      setFile(null);

      return;
    }

    // Store selected file
    setFile(selectedFile);

    // Clear previous results
    setResults([]);

    setMessage("");

    console.log("Selected file:", selectedFile);
  };

  // =========================
  // HANDLE UPLOAD
  // =========================

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a CSV or Excel file first.");

      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    try {
      // Start loading
      setLoading(true);

      setMessage("");

      // Send file to FastAPI
      const response = await fetch(
        "http://127.0.0.1:8000/feedback/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      // Check response status
      if (!response.ok) {
        throw new Error(
          `Upload failed: ${response.status}`
        );
      }

      // Read backend response
      const data = await response.json();

      console.log(
  "Backend response:",
  JSON.stringify(data, null, 2)
);
      // Store processed results
      if (Array.isArray(data.data)) {
        setResults(data.data);
      } else {
        setResults([]);
      }

      // Success message
      setMessage("File uploaded successfully!");

    } catch (error) {
      console.error("Upload error:", error);

      setMessage(
        "File upload failed. Please try again."
      );

    } finally {
      // Stop loading
      setLoading(false);
    }
  };

  // =========================
// DOWNLOAD FILTERED RESULTS
// =========================

const downloadFilteredResults = () => {
  if (filteredResults.length === 0) {
    alert("No feedback available to download.");
    return;
  }

  const headers = [
    "ID",
    "Comment",
    "Language",
    "Date",
    "Location",
  ];

  const csvRows = [
    headers.join(","),
    ...filteredResults.map((item) =>
      [
        item.comment_id,
        `"${(item.comment || "").replace(/"/g, '""')}"`,
        item.language,
        item.date,
        item.location,
      ].join(",")
    ),
  ];

  const csvContent = csvRows.join("\n");

  const blob = new Blob([csvContent], {
    type: "text/csv;charset=utf-8;",
  });

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = "filtered_feedback.csv";
  link.click();

  URL.revokeObjectURL(url);
};

  return (
    <div className="app">
      <Sidebar setActivePage={setActivePage} />

    <div className="main-content">

      {/* Your existing CivicLens content */}

  
       <Navbar />

    {/* Your existing CivicLens content */}
        {activePage === "dashboard" && <h1>Dashboard Page</h1>}

        {activePage === "upload" && <h1>Upload Feedback Page</h1>}

       {activePage === "feedback" && <h1>Feedback List Page</h1>}

      {activePage === "insights" && <h1>Insights Page</h1>}   

      {/* =========================
          HEADER
      ========================= */}

      <header className="header">

        <div className="header-container">

          <div className="brand">

            <div className="brand-icon">
              C
            </div>

            <div>

              <h1>CivicLens</h1>

              <p>
                Citizen Feedback & Policy Intelligence
              </p>

            </div>

          </div>

          <div className="portal-label">
            PUBLIC SERVICE PORTAL
          </div>

        </div>

      </header>


      {/* =========================
          MAIN CONTENT
      ========================= */}

      <main className="page-content">


        {/* =========================
            HERO SECTION
        ========================= */}

        <section className="hero-section">

          <span className="badge">
            CITIZEN FEEDBACK PLATFORM
          </span>

          <h2>
            Citizen Feedback Portal
          </h2>

          <p className="hero-text">

            Help improve policies and public services by
            providing valuable citizen feedback.

          </p>

        </section>


        {/* =========================
            UPLOAD CARD
        ========================= */}

        <section className="upload-card" id="upload">

          <div className="upload-icon">
            📄
          </div>

          <h3>
            Upload Feedback Data
          </h3>

          <p className="upload-description">

            Upload a CSV or Excel file containing citizen
            feedback to begin the analysis process.

          </p>


          {/* =========================
              FILE SELECTION
          ========================= */}

          <label className="file-label">

            <span>
              Choose CSV or Excel File
            </span>

            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileChange}
            />

          </label>


          {/* =========================
              SELECTED FILE
          ========================= */}

          {file && (

            <div className="selected-file">

              <span className="file-check">
                ✓
              </span>

              <div>

                <strong>
                  {file.name}
                </strong>

                <small>
                  File selected successfully
                </small>

              </div>

            </div>

          )}


          {/* =========================
              UPLOAD BUTTON
          ========================= */}

         <button
            className="upload-button"
            onClick={handleUpload}
           disabled={!file || loading}
          >

            {loading
              ? "Uploading..."
              : "Upload Feedback"
            }

          </button>


          {/* =========================
              STATUS MESSAGE
          ========================= */}

          {message && (

            <p className="upload-message">
              {message}
            </p>

          )}


          {/* =========================
              SUPPORTED FORMATS
          ========================= */}

          <p className="file-info">

            Supported formats: CSV, XLS, XLSX

          </p>

        </section>
          
         {/* =========================
    LANGUAGE DASHBOARD
========================= */}

{results.length > 0 && (
      <section className="language-dashboard" id="dashboard">

    <h2>Language Analysis</h2>

    {/* SUMMARY CARDS */}

    <div className="summary-cards">

      <StatCard
        title="Total Feedback"
        value={results.length}
        description="Uploaded feedback records"
      />

      <StatCard
        title="Languages Found"
        value={totalLanguages}
        description="Detected languages"
      />

    </div>

    {/* LANGUAGE DISTRIBUTION */}

    <div className="language-distribution">

      <h3>Language Distribution</h3>

      {Object.entries(languageCounts).map(
        ([language, count]) => (

          <div
            className="language-row"
            key={language}
          >

            <span className="language-name">
              {language}
            </span>

            <div className="language-bar-background">

              <div
                className="language-bar"
                style={{
                  width: `${(count / results.length) * 100}%`
                }}
              ></div>

            </div>

            <span className="language-count">
              {count}
            </span>

          </div>

        )
      )}

    </div>

  </section>
)}
{/* FEEDBACK TABLE */}

{results.length > 0 && (
  <FeedbackTable results={results} />
)}



          {/* =========================
    LOCATION DASHBOARD
========================= */}

{results.length > 0 && (
  <section className="location-dashboard">

    <h2>Location Analysis</h2>

    <div className="location-cards">

      {Object.entries(locationCounts).map(
        ([location, count]) => (

          <div
            className="location-card"
            key={location}
          >

            <h3>{location}</h3>

            <p>{count}</p>

            <span>
              Feedback Records
            </span>

          </div>

        )
      )}

    </div>

  </section>
)}           
            {/* =========================
    SENTIMENT DASHBOARD
========================= */}

{results.length > 0 && (
  <section className="sentiment-dashboard" id="insights">

    <h2>Sentiment Analysis</h2>

    {!hasSentimentData ? (

      <p>
        Sentiment analysis results are not available yet.
      </p>

    ) : (

      <div className="sentiment-cards">

        {Object.entries(sentimentCounts).map(
          ([sentiment, count]) => (

            <div
              className="sentiment-card"
              key={sentiment}
            >

              <h3>{sentiment}</h3>

              <p>{count}</p>

              <span>
                Feedback Records
              </span>

            </div>

          )
        )}

      </div>

    )}

  </section>
)}


        {/* =========================
            RESULTS SECTION
        ========================= */}

        {results.length > 0 && (

          <section className="results-section">

            {/* =========================
    FILTER CONTROLS
========================= */}

<div className="filter-controls">

  {/* SEARCH */}

  <input
    type="text"
    placeholder="Search feedback..."
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    className="search-input"
  />

  {/* LANGUAGE FILTER */}

  <select
    value={selectedLanguage}
    onChange={(e) => setSelectedLanguage(e.target.value)}
    className="filter-select"
  >

    {languages.map((language) => (
      <option key={language} value={language}>
        {language}
      </option>
    ))}

  </select>

  {/* LOCATION FILTER */}

  <select
    value={selectedLocation}
    onChange={(e) => setSelectedLocation(e.target.value)}
    className="filter-select"
  >

    {locations.map((location) => (
      <option key={location} value={location}>
        {location}
      </option>
    ))}

  </select>

  <button
    className="clear-filters-button"
    onClick={clearFilters}
  >
    Clear Filters
  </button>
   <button
  className="download-button"
  onClick={downloadFilteredResults}
>
  Download CSV
</button>

</div>

            <h2>
              Processed Feedback
            </h2>

            <p>
  Showing {filteredResults.length} of {results.length} feedback records
</p>


            <div className="results-table-container">

  <table className="results-table">

    <thead>
      <tr>
        <th>ID</th>
        <th>Comment</th>
        <th>Language</th>
        <th>Date</th>
        <th>Location</th>
      </tr>
    </thead>

    <tbody>

      {filteredResults.length > 0 ? (
        filteredResults.map((item, index) => (
          <tr key={item.comment_id || index}>
            <td>{item.comment_id}</td>
            <td>{item.comment}</td>
            <td>
              <span className="language-badge">
                {item.language}
              </span>
            </td>
            <td>{item.date}</td>
            <td>{item.location}</td>
          </tr>
        ))
      ) : (
        <tr>
          <td colSpan="5" className="no-results">
            No feedback found matching your search or filters.
          </td>
        </tr>
      )}

    </tbody>

  </table>

</div>

          </section>

        )}


        {/* =========================
            FEATURES
        ========================= */}

        <section className="features">


          {/* SECURE PROCESSING */}

          <div className="feature">

            <div className="feature-icon">
              🔒
            </div>

            <div>

              <h4>
                Secure Processing
              </h4>

              <p>

                Feedback is processed through the
                CivicLens backend.

              </p>

            </div>

          </div>


          {/* DATA-DRIVEN INSIGHTS */}

          <div className="feature">

            <div className="feature-icon">
              📊
            </div>

            <div>

              <h4>
                Data-Driven Insights
              </h4>

              <p>

                Transform citizen feedback into
                useful policy insights.

              </p>

            </div>

          </div>


          {/* HUMAN OVERSIGHT */}

          <div className="feature">

            <div className="feature-icon">
              👥
            </div>

            <div>

              <h4>
                Human Oversight
              </h4>

              <p>

                Keep people involved in final
                policy decisions.

              </p>

            </div>

          </div>

        </section>

      </main>


      {/* =========================
          FOOTER
      ========================= */}

      <footer className="footer">

        <div className="footer-line"></div>

        <p>

          CivicLens • Citizen Feedback Intelligence Platform

        </p>

        <span>

          Built for better public policy decisions

        </span>

      </footer>
      </div>

    </div>
  );
}

export default App;