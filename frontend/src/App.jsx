import { useEffect, useState } from "react";
import StatCard from "./components/StatCard";
import Navbar from "./components/Navbar";
import UploadBox from "./components/UploadBox";
import FeedbackTable from "./components/FeedbackTable";
import Sidebar from "./components/Sidebar";
import "./index.css";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function App() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTopic, setSelectedTopic] = useState("All");
const [selectedSentiment, setSelectedSentiment] = useState("All");
const [selectedLanguage, setSelectedLanguage] = useState("All");
const [selectedLocation, setSelectedLocation] = useState("All");
const [activePage, setActivePage] = useState("dashboard");
  useEffect(() => {
  fetch("http://127.0.0.1:8000/feedback/")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to fetch feedback");
      }

      return response.json();
    })
    .then((data) => {
  console.log("Feedback from backend:", data);
  console.log("FIRST FEEDBACK:", data[0]);
  console.log("TOPIC:", data[0]?.predicted_topic);
  console.log("TOPIC SCORE:", data[0]?.topic_score);

  setResults(data);
})
    .catch((error) => {
      console.error("Error fetching feedback:", error);
    });
}, []);
  
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
  const sentiment = item.predicted_sentiment;

  if (!sentiment) {
    return counts;
  }

  counts[sentiment] = (counts[sentiment] || 0) + 1;

  return counts;
}, {});

const hasSentimentData =
  Object.keys(sentimentCounts).length > 0;

 console.log(
  "SENTIMENT VALUES:",
  results.map((item) => ({
    comment_id: item.comment_id,
    keys: Object.keys(item),
    predicted_sentiment: item.predicted_sentiment,
    sentiment: item.sentiment
  }))
);

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

const topics = [
  "All",
  ...new Set(
    results.map((item) => item.predicted_topic).filter(Boolean)
  ),
];

const sentiments = [
  "All",
  ...new Set(
    results.map((item) => item.predicted_sentiment).filter(Boolean)
  ),
];

const totalFeedback = results.length;

const positiveCount = results.filter(
  (item) => item.predicted_sentiment?.toLowerCase() === "positive"
).length;

const negativeCount = results.filter(
  (item) => item.predicted_sentiment?.toLowerCase() === "negative"
).length;

const neutralCount = results.filter(
  (item) => item.predicted_sentiment?.toLowerCase() === "neutral"
).length;

const topicCount = new Set(
  results
    .map((item) => item.predicted_topic)
    .filter(Boolean)
).size;

const sentimentChartData = [
  {
    name: "Positive",
    value: positiveCount,
  },
  {
    name: "Negative",
    value: negativeCount,
  },
  {
    name: "Neutral",
    value: neutralCount,
  },
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
  
  const matchesTopic =
  selectedTopic === "All" ||
  item.predicted_topic === selectedTopic;

  const matchesSentiment =
  selectedSentiment === "All" ||
  item.predicted_sentiment === selectedSentiment;

  return (
    matchesSearch &&
    matchesLanguage &&
    matchesLocation &&
    matchesTopic &&
    matchesSentiment
  );
});


// =========================
// CLEAR FILTERS
// =========================

const clearFilters = () => {
  setSearchTerm("");
  setSelectedLanguage("All");
  setSelectedLocation("All");
  setSelectedTopic("All");
  setSelectedSentiment("All");
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
      // Fetch complete feedback data from database
const feedbackResponse = await fetch(
  "http://127.0.0.1:8000/feedback/"
);

if (!feedbackResponse.ok) {
  throw new Error("Failed to fetch feedback");
}

const feedbackData = await feedbackResponse.json();

setResults(feedbackData);

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

  
      <Navbar setActivePage={setActivePage} />

    {/* Your existing CivicLens content */}
        
      {/* =========================
          HEADER
      ========================= */}

      <header className="header">

        <div className="header-container">

          <div className="brand">

            <div className="brand-icon">
              
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
        {activePage === "upload" && (
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
        )}
          
         {/* =========================
                 LANGUAGE DASHBOARD
          ========================= */}
{activePage === "dashboard" && (
  <>

    {results.length > 0 && (
      <div className="stats-grid">

        <div className="stat-card">
          <h3>Total Feedback</h3>
          <div className="stat-value">{totalFeedback}</div>
        </div>

        <div className="stat-card">
          <h3>Positive</h3>
          <div className="stat-value">{positiveCount}</div>
        </div>

        <div className="stat-card">
          <h3>Negative</h3>
          <div className="stat-value">{negativeCount}</div>
        </div>

        <div className="stat-card">
          <h3>Neutral</h3>
          <div className="stat-value">{neutralCount}</div>
        </div>

        <div className="stat-card">
          <h3>Topics</h3>
          <div className="stat-value">{topicCount}</div>
        </div>

      </div>
    )}

    {results.length === 0 && (
      <p>No feedback uploaded yet. Please upload a file first.</p>
    )}

  </>
)}

{activePage === "dashboard" && results.length > 0 && (
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

{activePage === "feedback" && results.length > 0 && (
  <FeedbackTable results={results} />
)}



          {/* =========================
    LOCATION DASHBOARD
========================= */}

{activePage === "insights" && results.length > 0 && (
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

{activePage === "insights" && results.length > 0 && (
  <section className="sentiment-dashboard" id="insights">

    <h2>Sentiment Analysis</h2>

    {!hasSentimentData ? (

      <p>
        Sentiment analysis results are not available yet.
      </p>

    ) : (

      <div className="sentiment-cards">

        {["Positive", "Negative", "Neutral"].map(
          (sentiment) => {

            const count =
              sentimentCounts[sentiment] || 0;

            return (
              <div
                className={`sentiment-card ${sentiment.toLowerCase()}`}
                key={sentiment}
              >

                <h3>{sentiment}</h3>

                <p>{count}</p>

                <span>
                  Feedback Records
                </span>

              </div>
            );
          }
        )}

      </div>
    )}

  </section>
)}

        {/* =========================
            RESULTS SECTION
        ========================= */}
          {activePage === "feedback" && results.length > 0 && (
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

  {/* TOPIC FILTER */}

<select
  value={selectedTopic}
  onChange={(e) => setSelectedTopic(e.target.value)}
  className="filter-select"
>
  {topics.map((topic) => (
    <option key={topic} value={topic}>
      {topic}
    </option>
  ))}
</select>

{/* SENTIMENT FILTER */}

<select
  value={selectedSentiment}
  onChange={(e) => setSelectedSentiment(e.target.value)}
  className="filter-select"
>
  {sentiments.map((sentiment) => (
    <option key={sentiment} value={sentiment}>
      {sentiment}
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
    <th>Sentiment</th>
    <th>Topic</th>
    <th>Topic Score</th>
  </tr>
</thead>
  <tbody>
  {filteredResults.length > 0 ? (
    filteredResults.map((item, index) => (
      <tr key={item.comment_id || index}>

        <td>{item.comment_id}</td>

        <td>
          <div>{item.comment}</div>
        </td>

        <td>
          <span className="language-badge">
            {item.language || "—"}
          </span>
        </td>

        <td>{item.date || "—"}</td>

        <td>{item.location || "—"}</td>

        <td>
          <span
            className={`sentiment-badge ${
              item.predicted_sentiment
                ? item.predicted_sentiment.toLowerCase()
                : "not-available"
            }`}
          >
            {item.predicted_sentiment || "Not available"}
          </span>
        </td>

        <td>
          {item.predicted_topic || "—"}
        </td>

        <td>
          {item.topic_score !== null &&
          item.topic_score !== undefined
            ? Number(item.topic_score).toFixed(2)
            : "—"}
        </td>

      </tr>
    ))
  ) : (
    <tr>
      <td colSpan="8" className="no-results">
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
