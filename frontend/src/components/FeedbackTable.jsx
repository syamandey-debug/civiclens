function FeedbackTable({ results }) {
  return (
    <div className="feedback-table-container" id="feedback">
      <h2>Uploaded Feedback</h2>

      <table className="feedback-table">

        <thead>
          <tr>
            <th>Comment</th>
            <th>Language</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {results.map((item, index) => (
            <tr key={index}>

              <td>
                {item.comment || item.text || "N/A"}
              </td>

              <td>
                {item.language || "Unknown"}
              </td>

              <td>
                Detected
              </td>

            </tr>
          ))}
        </tbody>

      </table>

    </div>
  );
}

export default FeedbackTable;