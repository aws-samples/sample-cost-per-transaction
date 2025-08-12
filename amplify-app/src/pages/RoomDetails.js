import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { API, graphqlOperation } from 'aws-amplify';
import { getRoom } from '../graphql/queries';

const RoomDetails = () => {
  const { id } = useParams();
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRoomDetails();
  }, [id]);

  async function fetchRoomDetails() {
    try {
      const roomData = await API.graphql(graphqlOperation(getRoom, { id }));
      setRoom(roomData.data.getRoom);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching room details:', err);
      setError('Could not load room details. Please try again later.');
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="loading">Loading room details...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!room) {
    return <div className="not-found">Room not found</div>;
  }

  return (
    <div className="room-details">
      <div className="room-header">
        <h1>{room.name}</h1>
      </div>

      <div className="room-content">
        <div className="room-image-container">
          {room.imageUrl ? (
            <img src={room.imageUrl} alt={room.name} className="room-image" />
          ) : (
            <div className="placeholder-image">No Image Available</div>
          )}
        </div>

        <div className="room-info">
          <h2>Room Details</h2>
          <p className="room-description">{room.description}</p>
          
          <div className="room-specs">
            <div className="spec">
              <span className="spec-label">Price:</span>
              <span className="spec-value">${room.price} per night</span>
            </div>
            
            <div className="spec">
              <span className="spec-label">Capacity:</span>
              <span className="spec-value">{room.capacity} {room.capacity === 1 ? 'person' : 'people'}</span>
            </div>
            
            <div className="spec">
              <span className="spec-label">Availability:</span>
              <span className={`spec-value ${room.isAvailable ? 'available' : 'unavailable'}`}>
                {room.isAvailable ? 'Available' : 'Unavailable'}
              </span>
            </div>
          </div>

          {room.amenities && room.amenities.length > 0 && (
            <div className="amenities">
              <h3>Amenities</h3>
              <ul>
                {room.amenities.map((amenity, index) => (
                  <li key={index}>{amenity}</li>
                ))}
              </ul>
            </div>
          )}
          
          {room.isAvailable && (
            <Link to={`/booking/${room.id}`} className="book-now-btn">
              Book Now
            </Link>
          )}
        </div>
      </div>

      <div className="back-links">
        <Link to={`/hotel/${room.hotelID}`}>← Back to Hotel</Link>
      </div>
    </div>
  );
};

export default RoomDetails;