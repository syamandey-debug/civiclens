import { useState } from "react";

function FeedbackTable({ results }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [languageFilter, setLanguageFilter] = useState("All");
  const [sentimentFilter, setSentimentFilter] = useState("All");
  const [topicFilter, setTopicFilter] = useState("All");

  const getSentiment = (item) => {
    return item.sentiment || item.predicted_sentiment || "";
  };

  const filteredResults = results.filter((item) => {
    const comment = item.comment || item.text || "";
    const language = item.language || "";
    const sentiment = getSentiment(item);
    const topic = item.predicted_topic || "";

    const matchesSearch = comment
      .toLowerCase()
      .includes(searchTerm.toLowerCase());

    const matchesLanguage =
      languageFilter === "All" || language === languageFilter;

    const matchesSentiment =
      sentimentFilter === "All" || sentiment === sentimentFilter;

    const matchesTopic =
      topicFilter === "All" || topic === topicFilter;

    return (
      matchesSearch &&
      matchesLanguage &&
      matchesSentiment &&
      matchesTopic
    );
  });

  const languages = [
    ...new Set(
      results
        .map((item) => item.language)
        .filter(Boolean)
    ),
  ];

  const sentiments = [
    ...new Set(
      results
        .map((item) => getSentiment(item))
        .filter(Boolean)
    ),
  ];

  const topics = [
    ...new Set(
      results
        .map((item) => item.predicted_topic)
        .filter(Boolean)
    ),
  ];

  return (
    <div className="feedback-table-container" id="feedback">

      <h2>Uploaded Feedback</h2>

      {/* Search */}
      <div className="feedback-filters">

        <input
          type="text"
          placeholder="Search feedback..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        {/* Language */}
        <select
          value={languageFilter}
          onChange={(e) => setLanguageFilter(e.target.value)}
        >
          <option value="All">All Languages</option>

          {languages.map((language) => (
            <option key={language} value={language}>
              {language}
            </option>
          ))}
        </select>

        {/* Sentiment */}
        <select
          value={sentimentFilter}
          onChange={(e) => setSentimentFilter(e.target.value)}
        >
          <option value="All">All Sentiments</option>

          {sentiments.map((sentiment) => (
            <option key={sentiment} value={sentiment}>
              {sentiment}
            </option>
          ))}
        </select>

        {/* Topic */}
        <select
          value={topicFilter}
          onChange={(e) => setTopicFilter(e.target.value)}
        >
          <option value="All">All Topics</option>

          {topics.map((topic) => (
            <option key={topic} value={topic}>
              {topic}
            </option>
          ))}
        </select>

      </div>

      {/* Table */}
      <table className="feedback-table">

        <thead>
          <tr>
            <th>Comment</th>
            <th>Language</th>
            <th>Sentiment</th>
            <th>Topic</th>
            <th>Topic Score</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>

          {filteredResults.length > 0 ? (

            filteredResults.map((item, index) => (

              <tr key={index}>

                <td>
                  {item.comment || item.text || "N/A"}
                </td>

                <td>
                  {item.language || "Unknown"}
                </td>

                <td>
                  {getSentiment(item) || "Unknown"}
                </td>

                <td>
                  {item.predicted_topic || "Unknown"}
                </td>

                <td>
                  {item.topic_score != null
                    ? Number(item.topic_score).toFixed(2)
                    : "N/A"}
                </td>

                <td>
                  Detected
                </td>

              </tr>

            ))

          ) : (

            <tr>
              <td colSpan="6">
                No feedback found.
              </td>
            </tr>

          )}

        </tbody>

      </table>

    </div>
  );
}

export default FeedbackTable;