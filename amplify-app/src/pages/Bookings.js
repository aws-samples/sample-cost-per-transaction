import React, { useState, useEffect } from 'react';
import { API, graphqlOperation } from 'aws-amplify';
import { useLocation } from 'react-router-dom';
import { listBookings } from '../graphql/queries';
import { updateBooking } from '../graphql/mutations';
import './Bookings.css';

const Bookings = ({ user }) => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const location = useLocation();

  useEffect(() => {
    if (location.state?.success) {
      setSuccessMessage('Booking completed successfully!');
      // Clear the success message after 5 seconds
      const timer = setTimeout(() => {
        setSuccessMessage('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [location]);

  useEffect(() => {
    fetchBookings();
  }, [user]);

  async function fetchBookings() {
    if (!user) return;
    
    try {
      const filter = {
        userID: { eq: user.username }
      };
      
      const bookingData = await API.graphql(graphqlOperation(listBookings, { filter }));
      const bookingList = bookingData.data.listBookings.items;
      
      // Sort bookings by start date (most recent first)
      bookingList.sort((a, b) => new Date(b.startDate) - new Date(a.startDate));
      
      setBookings(bookingList);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching bookings:', err);
      setError('Could not load your bookings. Please try again later.');
      setLoading(false);
    }
  }

  const cancelBooking = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) {
      return;
    }
    
    try {
      await API.graphql(graphqlOperation(updateBooking, {
        input: {
          id: bookingId,
          status: 'CANCELLED'
        }
      }));
      
      // Update the local state
      setBookings(bookings.map(booking => 
        booking.id === bookingId 
          ? { ...booking, status: 'CANCELLED' } 
          : booking
      ));
      
      setSuccessMessage('Booking cancelled successfully!');
      // Clear the success message after 5 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 5000);
    } catch (err) {
      console.error('Error cancelling booking:', err);
      setError('Failed to cancel booking. Please try again.');
      // Clear the error message after 5 seconds
      setTimeout(() => {
        setError('');
      }, 5000);
    }
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'CONFIRMED':
        return 'status-confirmed';
      case 'PENDING':
        return 'status-pending';
      case 'CANCELLED':
        return 'status-cancelled';
      default:
        return '';
    }
  };

  if (loading) {
    return <div className="loading">Loading your bookings...</div>;
  }

  return (
    <div className="bookings-page">
      <h1>My Bookings</h1>
      
      {successMessage && (
        <div className="success-message">{successMessage}</div>
      )}
      
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      {bookings.length === 0 ? (
        <div className="no-bookings">
          <p>You don't have any bookings yet.</p>
        </div>
      ) : (
        <div className="bookings-list">
          {bookings.map(booking => (
            <div key={booking.id} className="booking-card">
              <div className="booking-header">
                <h2>Booking #{booking.id.substring(0, 8)}</h2>
                <span className={`booking-status ${getStatusClass(booking.status)}`}>
                  {booking.status}
                </span>
              </div>
              
              <div className="booking-details">
                <div className="booking-info">
                  <p><strong>Check-in:</strong> {formatDate(booking.startDate)}</p>
                  <p><strong>Check-out:</strong> {formatDate(booking.endDate)}</p>
                  <p><strong>Guest:</strong> {booking.guestName}</p>
                  <p><strong>Total Price:</strong> ${booking.totalPrice}</p>
                  
                  {booking.specialRequests && (
                    <div className="special-requests">
                      <p><strong>Special Requests:</strong></p>
                      <p>{booking.specialRequests}</p>
                    </div>
                  )}
                </div>
                
                {booking.status === 'CONFIRMED' && (
                  <div className="booking-actions">
                    <button 
                      onClick={() => cancelBooking(booking.id)}
                      className="cancel-booking-btn"
                    >
                      Cancel Booking
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Bookings;