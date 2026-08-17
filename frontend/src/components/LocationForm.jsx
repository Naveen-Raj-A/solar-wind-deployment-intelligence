import React, { useState } from 'react';

const LocationForm = ({ onSubmit, isLoading }) => {
  const [mode, setMode] = useState('name');
  const [formData, setFormData] = useState({
    location: '',
    latitude: '',
    longitude: '',
    available_land_area_km2: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const requestData = {
      available_land_area_km2: parseFloat(formData.available_land_area_km2)
    };
    if (mode === 'name') {
      requestData.location = formData.location;
    } else {
      requestData.latitude = parseFloat(formData.latitude);
      requestData.longitude = parseFloat(formData.longitude);
    }
    onSubmit(requestData);
  };

  return (
    <div className="form-card">
      <div className="form-group">
        <label>Location method</label>
        <div className="mode-toggle" style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <button className={`submit-btn ${mode === 'name' ? '' : 'inactive'}`} style={{ backgroundColor: mode === 'name' ? 'var(--navy)' : '#ccc' }} onClick={() => setMode('name')}>Location Name</button>
          <button className={`submit-btn ${mode === 'coords' ? '' : 'inactive'}`} style={{ backgroundColor: mode === 'coords' ? 'var(--navy)' : '#ccc' }} onClick={() => setMode('coords')}>Coordinates</button>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        {mode === 'name' ? (
          <div className="form-group">
            <label htmlFor="location">Location</label>
            <input className="form-control" type="text" id="location" name="location" value={formData.location} onChange={handleChange} required />
          </div>
        ) : (
          <>
            <div className="form-group">
              <label htmlFor="latitude">Latitude</label>
              <input className="form-control" type="number" step="any" id="latitude" name="latitude" value={formData.latitude} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="longitude">Longitude</label>
              <input className="form-control" type="number" step="any" id="longitude" name="longitude" value={formData.longitude} onChange={handleChange} required />
            </div>
          </>
        )}

        <div className="form-group">
          <label htmlFor="available_land_area_km2">Available Land for Deployment (km²)</label>
          <small style={{display: 'block', marginBottom: '5px', color: '#666'}}>Enter the amount of land you intend to use for the renewable-energy project.</small>
          <input className="form-control" type="number" step="any" id="available_land_area_km2" name="available_land_area_km2" value={formData.available_land_area_km2} onChange={handleChange} required min="0.01" />
        </div>

        <button type="submit" className="submit-btn" disabled={isLoading}>
          {isLoading ? 'Analysing Site...' : 'Analyse Site'}
        </button>
      </form>
    </div>
  );
};

export default LocationForm;
