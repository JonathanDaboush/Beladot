import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Navbar, Container, Nav, NavDropdown, Badge, Button } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';

const Header = () => {
  const { user, isAuthenticated, logout, currentView, getAvailableViews, switchView } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleViewSwitch = (view) => {
    switchView(view);
    
    const viewRoutes = {
      'customer': '/',
      'seller': '/seller',
      'cs-console': '/cs-console',
      'finance-console': '/finance',
      'transport-console': '/transport',
      'manager-console': '/manager',
      'analytics': '/analytics',
      'admin': '/admin',
    };
    
    navigate(viewRoutes[view] || '/');
  };

  const availableViews = isAuthenticated ? getAvailableViews(user?.role, user?.roles) : [];
  const isAdminImpersonating = user?.role === 'admin' && currentView !== 'admin';
  const currentViewLabel = availableViews.find(v => v.value === currentView)?.label || 'Home';
  const currentViewIcon = availableViews.find(v => v.value === currentView)?.icon || '🏠';

  return (
    <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
      <Container fluid>
        <Navbar.Brand as={Link} to="/" className="fw-bold">
          Beladot
        </Navbar.Brand>
        
        <Navbar.Toggle aria-controls="navbar-nav" />
        <Navbar.Collapse id="navbar-nav">
          <Nav className="me-auto">
            {isAuthenticated && availableViews.length > 1 && (
              <NavDropdown 
                title={`${currentViewIcon} ${currentViewLabel}`} 
                id="view-switcher-dropdown"
              >
                {availableViews.map((view, idx) => (
                  view.disabled ? (
                    <NavDropdown.Divider key={idx} />
                  ) : (
                    <NavDropdown.Item
                      key={idx}
                      active={view.value === currentView}
                      onClick={() => handleViewSwitch(view.value)}
                    >
                      {view.icon} {view.label}
                    </NavDropdown.Item>
                  )
                ))}
              </NavDropdown>
            )}
          </Nav>

          <Nav>
            {isAuthenticated ? (
              <>
                {isAdminImpersonating && (
                  <Badge bg="warning" text="dark" className="me-3 align-self-center">
                    Admin Mode: Viewing as {currentView}
                  </Badge>
                )}
                
                <NavDropdown 
                  title={
                    <span>
                      <span className="me-2">
                        {user?.first_name || user?.email}
                      </span>
                    </span>
                  }
                  id="user-dropdown"
                  align="end"
                >
                  <NavDropdown.ItemText>
                    <div className="fw-bold">{user?.email}</div>
                    <small className="text-muted">{user?.role?.replace('_', ' ')}</small>
                  </NavDropdown.ItemText>
                  <NavDropdown.Divider />
                  <NavDropdown.Item as={Link} to="/profile">
                    My Profile
                  </NavDropdown.Item>
                  <NavDropdown.Item as={Link} to="/orders">
                    My Orders
                  </NavDropdown.Item>
                  {user?.role === 'seller' && (
                    <NavDropdown.Item as={Link} to="/seller">
                      Seller Portal
                    </NavDropdown.Item>
                  )}
                  <NavDropdown.Divider />
                  <NavDropdown.Item onClick={handleLogout}>
                    Logout
                  </NavDropdown.Item>
                </NavDropdown>
              </>
            ) : (
              <>
                <Button 
                  variant="outline-light" 
                  as={Link} 
                  to="/login" 
                  className="me-2"
                >
                  Sign In
                </Button>
                <Button 
                  variant="primary" 
                  as={Link} 
                  to="/register"
                >
                  Sign Up
                </Button>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header;
