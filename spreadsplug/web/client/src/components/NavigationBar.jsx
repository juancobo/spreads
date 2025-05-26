import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

/**
 * Modern navigation bar component using Bootstrap 5
 */
function NavigationBar({ workflows, selectedWorkflow, configuration, connected, onError }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const handleLogout = async () => {
    try {
      // Implement logout logic here
      window.location.href = '/logout';
    } catch (error) {
      onError?.(error);
    }
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
      <div className="container-fluid">
        <Link className="navbar-brand d-flex align-items-center" to="/">
          <i className="fas fa-book me-2"></i>
          Spreads
        </Link>

        {/* Connection Status Indicator */}
        <div className="navbar-text me-3 d-none d-md-block">
          <span className={`badge ${connected ? 'bg-success' : 'bg-danger'}`}>
            <i className={`fas ${connected ? 'fa-wifi' : 'fa-wifi'} me-1`}></i>
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        <button
          className="navbar-toggler"
          type="button"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-controls="navbarNav"
          aria-expanded={isMenuOpen}
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className={`collapse navbar-collapse ${isMenuOpen ? 'show' : ''}`} id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <Link 
                className={`nav-link ${isActive('/') ? 'active' : ''}`} 
                to="/"
              >
                <i className="fas fa-list me-1"></i>
                Workflows
              </Link>
            </li>
            <li className="nav-item">
              <Link 
                className={`nav-link ${isActive('/workflow/new') ? 'active' : ''}`} 
                to="/workflow/new"
              >
                <i className="fas fa-plus me-1"></i>
                New Workflow
              </Link>
            </li>
            {selectedWorkflow && (
              <>
                <li className="nav-item">
                  <Link 
                    className={`nav-link ${location.pathname.includes('/capture') ? 'active' : ''}`} 
                    to={`/workflow/${selectedWorkflow.id}/capture`}
                  >
                    <i className="fas fa-camera me-1"></i>
                    Capture
                  </Link>
                </li>
                <li className="nav-item">
                  <Link 
                    className={`nav-link ${location.pathname.includes('/submit') ? 'active' : ''}`} 
                    to={`/workflow/${selectedWorkflow.id}/submit`}
                  >
                    <i className="fas fa-upload me-1"></i>
                    Submit
                  </Link>
                </li>
              </>
            )}
          </ul>

          <ul className="navbar-nav">
            <li className="nav-item">
              <Link 
                className={`nav-link ${isActive('/logs') ? 'active' : ''}`} 
                to="/logs"
              >
                <i className="fas fa-file-alt me-1"></i>
                Logs
              </Link>
            </li>
            <li className="nav-item dropdown">
              <a
                className="nav-link dropdown-toggle"
                href="#"
                id="navbarDropdown"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                <i className="fas fa-cog me-1"></i>
                Settings
              </a>
              <ul className="dropdown-menu dropdown-menu-end">
                <li>
                  <Link className="dropdown-item" to="/preferences">
                    <i className="fas fa-sliders-h me-2"></i>
                    Preferences
                  </Link>
                </li>
                <li><hr className="dropdown-divider" /></li>
                <li>
                  <button className="dropdown-item" onClick={handleLogout}>
                    <i className="fas fa-sign-out-alt me-2"></i>
                    Logout
                  </button>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default NavigationBar;
