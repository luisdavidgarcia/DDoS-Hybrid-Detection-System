// src/components/Visualization.js
import React, { useRef, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const Visualization = ({ data }) => {
  const chartRef = useRef(null);

  const chartData = {
    labels: data.labels || [],
    datasets: [
      {
        label: 'Predictions',
        data: data.values || [],
        borderColor: 'rgba(75,192,192,1)',
        fill: false,
      },
    ],
  };

  useEffect(() => {
    const chart = chartRef.current?.chartInstance;

    return () => {
      if (chart) {
        chart.destroy();
      }
    };
  }, []);

  if (!data || !data.labels || !data.values) {
    return <div>Invalid data</div>;
  }

  return (
    <div>
      <h2>Visualization</h2>
      <Line ref={chartRef} data={chartData} />
    </div>
  );
};

export default Visualization;
