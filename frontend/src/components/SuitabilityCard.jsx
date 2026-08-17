import React from 'react';

const SuitabilityCard = ({ assessment }) => {
  if (!assessment) return null;
  return (
    <div className="card">
      <h3>Overall Suitability</h3>
      <div className="score-display">{assessment.normalized_score} / 100</div>
      <p style={{textAlign: 'center', fontWeight: 'bold'}}>{assessment.recommendation}</p>
    </div>
  );
};

export default SuitabilityCard;
