import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { API, graphqlOperation } from 'aws-amplify';
import { getRoom } from '../graphql/queries';
import { createBooking } from '../graphql/mutations';
import './BookingForm.css';

const BookingForm = ({ user }) => {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    startDate: '',
    endDate: '',
    guestName: '',
    guestEmail: '',
    specialRequests: ''
  });
  const [totalPrice, setTotalPrice] = useState(0);
  const [nights, setNights] = useState(0);

  useEffect(() => {
    fetchRoomDetails();
  }, [roomId]);

  useEffect(() => {
    if (user) {
      setFormData(prevState => ({
        ...prevState,
        guestName: user.attributes?.name || user.username,
        guestEmail: user.attributes?.email || ''
      }));
    }
  }, [user]);

  useEffect(() => {
    calculatePrice();
  }, [formData.startDate, formData.endDate, room]);

  async function fetchRoomDetails() {
    try {
      const roomData = await API.graphql(graphqlOperation(getRoom, { id: roomId }));
      const fetchedRoom = roomData.data.getRoom;
      
      if (!fetchedRoom || !fetchedRoom.isAvailable) {
        setError('This room is not available for booking.');
        setLoading(false);
        return;
      }
      
      setRoom(fetchedRoom);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching room details:', err);
      setError('Could not load room details. Please try again later.');
      setLoading(false);
    }
  }

  const calculatePrice = () => {
    if (room && formData.startDate && formData.endDate) {
      const start = new Date(formData.startDate);
      const end = new Date(formData.endDate);
      
      if (start && end && end > start) {
        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        setNights(diffDays);
        setTotalPrice(room.price * diffDays);
      } else {
        setNights(0);
        setTotalPrice(0);
      }
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!room || !formData.startDate || !formData.endDate) {
      setError('Please fill in all required fields.');
      return;
    }
    
    const start = new Date(formData.startDate);
    const end = new Date(formData.endDate);
    
    if (end <= start) {
      setError('Check-out date must be after check-in date.');
      return;
    }
    
    try {
      const bookingInput = {
        roomID: roomId,
        userID: user.username,
        startDate: formData.startDate,
        endDate: formData.endDate,
        totalPrice: totalPrice,
        status: 'CONFIRMED',
        guestName: formData.guestName,
        guestEmail: formData.guestEmail,
        specialRequests: formData.specialRequests || null
      };
      
      await API.graphql(graphqlOperation(createBooking, { input: bookingInput }));
      navigate('/bookings', { state: { success: true } });
    } catch (err) {
      console.error('Error creating booking:', err);
      setError('Failed to create booking. Please try again.');
    }
  };

  if (loading) {
    return <div className="loading">Loading booking form...</div>;
  }

  if (error) {
    return (
      <div className="booking-error">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate(-1)}>Go Back</button>
      </div>
    );
  }

  return (
    <div className="booking-form-container">
      <h1>Book Your Stay</h1>
      
      <div className="room-summary">
        <h2>{room.name}</h2>
        <p className="price">${room.price} per night</p>
      </div>
      
      <form onSubmit={handleSubmit} className="booking-form">
        <div className="form-group">
          <label htmlFor="startDate">Check-in Date:</label>
          <input
            type="date"
            id="startDate"
            name="startDate"
            value={formData.startDate}
            onChange={handleChange}
            min={new Date().toISOString().split('T')[0]}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="endDate">Check-out Date:</label>
          <input
            type="date"
            id="endDate"
            name="endDate"
            value={formData.endDate}
            onChange={handleChange}
            min={formData.startDate || new Date().toISOString().split('T')[0]}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="guestName">Guest Name:</label>
          <input
            type="text"
            id="guestName"
            name="guestName"
            value={formData.guestName}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="guestEmail">Email:</label>
          <input
            type="email"
            id="guestEmail"
            name="guestEmail"
            value={formData.guestEmail}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="specialRequests">Special Requests:</label>
          <textarea
            id="specialRequests"
            name="specialRequests"
            value={formData.specialRequests}
            onChange={handleChange}
            rows="4"
          />
        </div>
        
        {nights > 0 && (
          <div className="price-summary">
            <h3>Price Summary</h3>
            <div className="price-row">
              <span>${room.price} x {nights} nights</span>
              <span>${totalPrice}</span>
            </div>
            <div className="price-total">
              <span>Total</span>
              <span>${totalPrice}</span>
            </div>
          </div>
        )}
        
        <div className="form-actions">
          <button type="button" onClick={() => navigate(-1)} className="cancel-btn">
            Cancel
          </button>
          <button type="submit" className="submit-btn" disabled={!formData.startDate || !formData.endDate || nights <= 0}>
            Complete Booking
          </button>
        </div>
      </form>
    </div>
  );
};

export default BookingForm;