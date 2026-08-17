import React from 'react';

const EnergyYield = ({ yieldData }) => {
  return (
    <div className="card">
      <h3>Energy Yield</h3>
      <p>Technology: {yieldData?.technology ?? 'N/A'}</p>
      <p>Capacity: {yieldData?.installed_capacity_mw ?? 'N/A'} MW</p>
      <p>Annual Energy: {yieldData?.annual_energy_mwh ?? 'N/A'} MWh</p>
      {yieldData?.solar?.capacity_factor && <p>Solar Capacity Factor: {yieldData.solar.capacity_factor}</p>}
      {yieldData?.wind?.capacity_factor && <p>Wind Capacity Factor: {yieldData.wind.capacity_factor}</p>}
    </div>
  );
};

export default EnergyYield;
