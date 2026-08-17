import React from 'react';

const TechnicalAssessment = ({ tech }) => {
  return (
    <div className="card">
      <h3>Technical Feasibility</h3>
      <p className={tech?.feasibility_status === 'FEASIBLE' ? 'status-feasible' : 'status-not-feasible'}>
        {tech?.feasibility_status}
      </p>
      <p>Score: {tech?.feasibility_score ?? 'N/A'}</p>
      <p>Passed: {tech?.hard_constraints_passed ?? 0}</p>
      <p>Failed: {tech?.hard_constraints_failed ?? 0}</p>
    </div>
  );
};

export default TechnicalAssessment;
