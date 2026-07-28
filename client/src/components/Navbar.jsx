import { useState } from 'react';
import { NavLink } from 'react-router-dom';

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="nav">
      <div className="nav-inner">
        <NavLink to="/" className="nav-brand">
          <div className="nav-brand-icon">🧬</div>
          KidneyDX
        </NavLink>
        <button className="nav-toggle" onClick={() => setIsOpen(!isOpen)}>
          ☰
        </button>
        <ul className={`nav-links ${isOpen ? 'open' : ''}`}>
          <li>
            <NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')}>
              Home
            </NavLink>
          </li>
          <li>
            <NavLink to="/diagnosis" className={({ isActive }) => (isActive ? 'active' : '')}>
              Diagnosis
            </NavLink>
          </li>
          <li>
            <NavLink to="/analytics" className={({ isActive }) => (isActive ? 'active' : '')}>
              Analytics
            </NavLink>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
