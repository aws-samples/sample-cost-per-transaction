import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { API, graphqlOperation } from 'aws-amplify';
import { getHotel } from '../graphql/queries';
import './HotelDetails.css';

const HotelDetails = () => {
  const { id } = useParams();
  const [hotel, setHotel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHotelDetails();
  }, [id]);

  async function fetchHotelDetails() {
    try {
      const hotelData = await API.graphql(graphqlOperation(getHotel, { id }));
      setHotel(hotelData.data.getHotel);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching hotel details:', err);
      setError('Could not load hotel details. Please try again later.');
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="loading">Loading hotel details...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!hotel) {
    return <div className="not-found">Hotel not found</div>;
  }

  return (
    <div className="hotel-details">
      <div className="hotel-header">
        <h1>{hotel.name}</h1>
        <p className="hotel-address">{hotel.address}, {hotel.city}</p>
      </div>

      <div className="hotel-content">
        <div className="hotel-image-container">
          {hotel.imageUrl ? (
            <img src={hotel.imageUrl} alt={hotel.name} className="hotel-image" />
          ) : (
            <div className="placeholder-image">No Image Available</div>
          )}
        </div>

        <div className="hotel-info">
          <h2>About this hotel</h2>
          <p className="hotel-description">{hotel.description}</p>
        </div>
      </div>

      <div className="rooms-section">
        <h2>Available Rooms</h2>
        {hotel.rooms && hotel.rooms.items.length > 0 ? (
          <div className="room-list">
            {hotel.rooms.items
              .filter(room => room.isAvailable)
              .map(room => (
                <div key={room.id} className="room-card">
                  <div className="room-image-container">
                    {room.imageUrl ? (
                      <img src={room.imageUrl} alt={room.name} className="room-image" />
                    ) : (
                      <div className="placeholder-image">No Image</div>
                    )}
                  </div>
                  <div className="room-info">
                    <h3>{room.name}</h3>
                    <p className="room-description">{room.description.substring(0, 100)}...</p>
                    <p className="room-capacity">Capacity: {room.capacity} {room.capacity === 1 ? 'person' : 'people'}</p>
                    <p className="room-price">${room.price} per night</p>
                    <Link to={`/room/${room.id}`} className="view-room-btn">
                      View Room
                    </Link>
                  </div>
                </div>
              ))}
          </div>
        ) : (
          <p>No rooms available at this hotel.</p>
        )}
      </div>

      <div className="back-link">
        <Link to="/">← Back to Hotels</Link>
      </div>
    </div>
  );
};

export default HotelDetails;