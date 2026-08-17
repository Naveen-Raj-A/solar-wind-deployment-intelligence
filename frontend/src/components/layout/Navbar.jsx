import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => (
  <nav className="navbar" style={{ padding: '20px 60px', position: 'sticky', top: 0, zIndex: 1000, background: 'var(--white)', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <div style={{ fontWeight: '800', fontSize: '1.5rem', color: 'var(--navy)' }}>SOLAR-WIND INTEL</div>
    <div className="nav-links" style={{ display: 'flex', gap: '30px', alignItems: 'center' }}>
      <Link to="/" style={{ textDecoration: 'none', color: 'var(--text)' }}>Platform</Link>
      <a href="#capabilities" style={{ textDecoration: 'none', color: 'var(--text)' }}>Capabilities</a>
      <a href="#how-it-works" style={{ textDecoration: 'none', color: 'var(--text)' }}>How It Works</a>
      <Link to="/analysis" className="btn btn-primary">Start Analysis</Link>
    </div>
  </nav>
);

export default Navbar;
