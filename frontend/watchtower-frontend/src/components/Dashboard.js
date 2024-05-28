// src/components/Dashboard.js
import React from 'react';
import './Dashboard.css';
import Visualization from './Visualization';
import Explanation from './Explanation';
import DataUpload from './DataUpload';

const Dashboard = () => {
  const dummyData = {
    labels: ['January', 'February', 'March', 'April', 'May'],
    values: [65, 59, 80, 81, 56],
  };

  const dummyPrediction = "Sample prediction";

  return (
    <div className="dashboard">
      <h1>Watchtower Dashboard</h1>
      <div className="visualization">
        <Visualization data={dummyData} />
      </div>
      <div className="explanation">
        <Explanation prediction={dummyPrediction} />
      </div>
      <div className="data-upload">
        <DataUpload />
      </div>
    </div>
  );
};

export default Dashboard;
