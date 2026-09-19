function UploadBox({
  file,
  setFile,
  handleUpload,
  loading
}) {
  return (
    <div className="upload-box">

      <input
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button
        onClick={handleUpload}
        disabled={!file || loading}
      >
        {loading ? "Uploading..." : "Upload Feedback"}
      </button>

    </div>
  );
}

export default UploadBox;