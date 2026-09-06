import { useState } from "react";
import "./index.css";

function App() {
  const [file, setFile] = useState(null);

  // Handle file selection
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

    console.log("Selected file:", selectedFile);
  };

  // Handle upload button
  const handleUpload = async () => {
    if (!file) {
      alert("Please select a CSV or Excel file first.");
      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(
      "http://127.0.0.1:8000/feedback/upload",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    console.log(data);

    alert("File uploaded successfully!");
  };

  return (
    <div className="app">

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

      <main className="main-content">

        {/* Hero Section */}

        <section className="hero-section">

          <span className="badge">
            CITIZEN FEEDBACK PLATFORM
          </span>

          <h2>
            Citizen Feedback Portal
          </h2>

          <p className="hero-text">
            Help improve policies and public services by providing
            valuable citizen feedback.
          </p>

        </section>


        {/* =========================
            UPLOAD CARD
        ========================= */}

        <section className="upload-card">

          <div className="upload-icon">
            📄
          </div>

          <h3>
            Upload Feedback Data
          </h3>

          <p className="upload-description">
            Upload a CSV or Excel file containing citizen feedback
            to begin the analysis process.
          </p>


          {/* File Selection */}

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


          {/* Selected File */}

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


          {/* Upload Button */}

          <button
            className="upload-button"
            onClick={handleUpload}
          >
            Upload Feedback
          </button>


          {/* Supported Formats */}

          <p className="file-info">
            Supported formats: CSV, XLS, XLSX
          </p>

        </section>


        {/* =========================
            FEATURES
        ========================= */}

        <section className="features">

          {/* Secure Processing */}

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


          {/* Data Driven */}

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


          {/* Human Oversight */}

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
  );
}

export default App;