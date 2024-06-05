// src/components/DataUpload.js
import React, { useState } from 'react';
import axios from 'axios';

const DataUpload = () => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      await axios.post('/upload', formData);
      alert('File uploaded successfully');
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  return (
    <div>
      <h2>Upload Data</h2>
      <input type="file" onChange={handleFileChange} accept=".csv"/>
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
};

export default DataUpload;
