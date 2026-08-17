import React from 'react';

const RecommendationCard = ({ rec }) => {
  return (
    <div className="card">
      <h3>Final Recommendation</h3>
      <p>Recommended Tech: <strong>{rec?.recommended_technology}</strong></p>
      <p>Capacity: {rec?.recommended_capacity_mw ?? 'N/A'} MW</p>
      <p>Expansion Status: {rec?.expansion_status ?? 'N/A'}</p>
      <p>Remarks: {rec?.optimization_remarks ?? 'N/A'}</p>
    </div>
  );
};

export default RecommendationCard;
