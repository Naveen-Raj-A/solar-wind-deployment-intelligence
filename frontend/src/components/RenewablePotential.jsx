import React from 'react';

const RenewablePotential = ({ assessment, deployment }) => {
  return (
    <div className="card">
      <h3>Renewable Potential</h3>
      <p>Recommended Tech: <strong>{deployment?.recommended_technology}</strong></p>
      <p>Solar Score: {assessment?.solar_score ?? 'N/A'}</p>
      <p>Wind Score: {assessment?.wind_score ?? 'N/A'}</p>
    </div>
  );
};

export default RenewablePotential;
