import React, { useState } from 'react';
import { API, graphqlOperation } from 'aws-amplify';
import { createHotel, createRoom } from '../graphql/mutations';

const AdminTools = () => {
  const [activeTab, setActiveTab] = useState('hotels');
  const [hotelFormData, setHotelFormData] = useState({
    name: '',
    description: '',
    address: '',
    city: '',
    imageUrl: ''
  });
  const [roomFormData, setRoomFormData] = useState({
    hotelID: '',
    name: '',
    description: '',
    price: '',
    imageUrl: '',
    capacity: '',
    amenities: '',
    isAvailable: true
  });
  const [message, setMessage] = useState('');

  const handleHotelChange = (e) => {
    const { name, value } = e.target;
    setHotelFormData({
      ...hotelFormData,
      [name]: value
    });
  };

  const handleRoomChange = (e) => {
    const { name, value } = e.target;
    setRoomFormData({
      ...roomFormData,
      [name]: name === 'price' || name === 'capacity' ? parseFloat(value) : value
    });
  };

  const handleHotelSubmit = async (e) => {
    e.preventDefault();
    try {
      await API.graphql(graphqlOperation(createHotel, { input: hotelFormData }));
      setMessage('Hotel created successfully!');
      setHotelFormData({
        name: '',
        description: '',
        address: '',
        city: '',
        imageUrl: ''
      });
    } catch (error) {
      console.error('Error creating hotel:', error);
      setMessage('Error creating hotel. Please try again.');
    }
  };

  const handleRoomSubmit = async (e) => {
    e.preventDefault();
    try {
      const roomInput = {
        ...roomFormData,
        price: parseFloat(roomFormData.price),
        capacity: parseInt(roomFormData.capacity),
        amenities: roomFormData.amenities.split(',').map(item => item.trim())
      };
      await API.graphql(graphqlOperation(createRoom, { input: roomInput }));
      setMessage('Room created successfully!');
      setRoomFormData({
        hotelID: '',
        name: '',
        description: '',
        price: '',
        imageUrl: '',
        capacity: '',
        amenities: '',
        isAvailable: true
      });
    } catch (error) {
      console.error('Error creating room:', error);
      setMessage('Error creating room. Please try again.');
    }
  };

  return (
    <div className="admin-tools">
      <h1>Admin Tools</h1>
      
      <div className="tabs">
        <button 
          className={activeTab === 'hotels' ? 'active' : ''} 
          onClick={() => setActiveTab('hotels')}
        >
          Manage Hotels
        </button>
        <button 
          className={activeTab === 'rooms' ? 'active' : ''} 
          onClick={() => setActiveTab('rooms')}
        >
          Manage Rooms
        </button>
      </div>
      
      {message && <div className="message">{message}</div>}
      
      {activeTab === 'hotels' && (
        <div className="tab-content">
          <h2>Add New Hotel</h2>
          <form onSubmit={handleHotelSubmit}>
            <div className="form-group">
              <label>Name:</label>
              <input 
                type="text" 
                name="name" 
                value={hotelFormData.name} 
                onChange={handleHotelChange} 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Description:</label>
              <textarea 
                name="description" 
                value={hotelFormData.description} 
                onChange={handleHotelChange} 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Address:</label>
              <input 
                type="text" 
                name="address" 
                value={hotelFormData.address} 
                onChange={handleHotelChange} 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>City:</label>
              <input 
                type="text" 
                name="city" 
                value={hotelFormData.city} 
                onChange={handleHotelChange} 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Image URL:</label>
              <input 
                type="text" 
                name="imageUrl" 
                value={hotelFormData.imageUrl} 
                onChange={handleHotelChange} 
              />
            </div>
            
            <button type="submit">Add Hotel</button>
          </form>
        </div>
      )}
      
      {activeTab === 'rooms' && (
        <div className="tab-content">
          <h2>Add New Room</h2>
          <form onSubmit={handleRoomSubmit}>
            <div className="form-group">
              <label>Hotel ID:</label>
              <input 
                type="text" 
                name="hotelID" 
                value={roomFormData.hotelID} 
                onChange={handleRoomChange} 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Name:</label>
              <input 
                type="text" 
                name="name" 
                value={roomFormData.name} 
                onChange={handleRoomChange} 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Description:</label>
              <textarea 
                name="description" 
                value={roomFormData.description} 
                onChange={handleRoomChange} 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Price:</label>
              <input 
                type="number" 
                name="price" 
                value={roomFormData.price} 
                onChange={handleRoomChange} 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Image URL:</label>
              <input 
                type="text" 
                name="imageUrl" 
                value={roomFormData.imageUrl} 
                onChange={handleRoomChange} 
              />
            </div>
            
            <div className="form-group">
              <label>Capacity:</label>
              <input 
                type="number" 
                name="capacity" 
                value={roomFormData.capacity} 
                onChange={handleRoomChange} 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Amenities (comma-separated):</label>
              <input 
                type="text" 
                name="amenities" 
                value={roomFormData.amenities} 
                onChange={handleRoomChange} 
                required 
              />
            </div>
            
            <div className="form-group">
              <label>Available:</label>
              <select 
                name="isAvailable" 
                value={roomFormData.isAvailable} 
                onChange={handleRoomChange}
              >
                <option value={true}>Yes</option>
                <option value={false}>No</option>
              </select>
            </div>
            
            <button type="submit">Add Room</button>
          </form>
        </div>
      )}
    </div>
  );
};

export default AdminTools;