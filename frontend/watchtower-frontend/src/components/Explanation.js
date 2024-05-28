// src/components/Explanation.js
import React, { useState } from 'react';
import axios from 'axios';

const Explanation = ({ prediction }) => {
  const [explanation, setExplanation] = useState('');

  const getExplanation = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/get_explanation/', { prediction });
      setExplanation(response.data.explanation);
    } catch (error) {
      console.error("Error fetching explanation:", error);
      setExplanation('Failed to get explanation');
    }
  };

  return (
    <div>
      <h2>Explanation</h2>
      <button onClick={getExplanation}>Get Explanation</button>
      <p>{explanation}</p>
    </div>
  );
};

export default Explanation;
