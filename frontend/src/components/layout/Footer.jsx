import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => (
  <footer className="footer">
    <div>
        <h3>SOLAR-WIND INTEL</h3>
        <p>AI-powered renewable energy site assessment & deployment planning.</p>
    </div>
    <div><h4>Platform</h4><p>Capabilities</p><p>How It Works</p></div>
    <div><h4>Intelligence</h4><p>Solar</p><p>Wind</p><p>GIS</p></div>
    <div><h4>Resources</h4><p>Reports</p><p>Documentation</p></div>
    <div style={{gridColumn: '1/-1', marginTop: '20px', borderTop: '1px solid #333', paddingTop: '20px'}}>
        © 2026 Solar & Wind Deployment Intelligence
    </div>
  </footer>
);

export default Footer;
