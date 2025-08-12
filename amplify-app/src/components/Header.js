import React from 'react';
import { Link } from 'react-router-dom';

const Header = ({ user, signOut, isAdmin }) => {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="logo">
            <Link to="/">Hotel Booking App</Link>
          </div>
          <nav className="nav">
            <ul>
              <li>
                <Link to="/">Home</Link>
              </li>
              <li>
                <Link to="/bookings">My Bookings</Link>
              </li>
              {isAdmin && (
                <li>
                  <Link to="/admin">Admin</Link>
                </li>
              )}
              <li className="user-info">
                <span>Hello, {user.username}</span>
                <button onClick={signOut}>Sign out</button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;