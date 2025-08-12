import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { Amplify } from 'aws-amplify';
import { withAuthenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import awsExports from './aws-exports';
import Header from './components/Header';
import Home from './pages/Home';
import HotelDetails from './pages/HotelDetails';
import RoomDetails from './pages/RoomDetails';
import BookingForm from './pages/BookingForm';
import Bookings from './pages/Bookings';
import AdminTools from './components/AdminTools';
import './App.css';

Amplify.configure(awsExports);

function App({ signOut, user }) {
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // Check if user has admin group
    const checkAdminStatus = async () => {
      try {
        const groups = user.signInUserSession.accessToken.payload['cognito:groups'] || [];
        setIsAdmin(groups.includes('Admin'));
      } catch (error) {
        console.error('Error checking admin status:', error);
        setIsAdmin(false);
      }
    };

    checkAdminStatus();
  }, [user]);

  return (
    <Router>
      <div className="app">
        <Header user={user} signOut={signOut} isAdmin={isAdmin} />
        <div className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/hotel/:id" element={<HotelDetails />} />
            <Route path="/room/:id" element={<RoomDetails />} />
            <Route path="/booking/:roomId" element={<BookingForm user={user} />} />
            <Route path="/bookings" element={<Bookings user={user} />} />
            {isAdmin && <Route path="/admin" element={<AdminTools />} />}
          </Routes>
        </div>
        <footer className="footer">
          <div className="container">
            <p>&copy; {new Date().getFullYear()} Hotel Booking App</p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default withAuthenticator(App);