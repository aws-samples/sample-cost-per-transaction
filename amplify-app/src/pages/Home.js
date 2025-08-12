import React, { useState, useEffect } from 'react';
import { API, graphqlOperation } from 'aws-amplify';
import { Link } from 'react-router-dom';
import { listHotels } from '../graphql/queries';

const Home = () => {
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredHotels, setFilteredHotels] = useState([]);

  useEffect(() => {
    fetchHotels();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const filtered = hotels.filter(hotel => 
        hotel.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        hotel.city.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredHotels(filtered);
    } else {
      setFilteredHotels(hotels);
    }
  }, [searchTerm, hotels]);

  async function fetchHotels() {
    try {
      const hotelData = await API.graphql(graphqlOperation(listHotels));
      const hotelList = hotelData.data.listHotels.items;
      setHotels(hotelList);
      setFilteredHotels(hotelList);
      setLoading(false);
    } catch (error) {
      console.log('Error fetching hotels:', error);
      setLoading(false);
    }
  }

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  if (loading) {
    return <div className="loading">Loading hotels...</div>;
  }

  return (
    <div className="home-page">
      <div className="search-container">
        <input
          type="text"
          placeholder="Search hotels by name or city..."
          value={searchTerm}
          onChange={handleSearchChange}
          className="search-input"
        />
      </div>

      <h1>Available Hotels</h1>
      
      {filteredHotels.length === 0 ? (
        <p>No hotels found. Please try a different search.</p>
      ) : (
        <div className="hotel-grid">
          {filteredHotels.map(hotel => (
            <div key={hotel.id} className="hotel-card">
              <div className="hotel-image">
                {hotel.imageUrl ? (
                  <img src={hotel.imageUrl} alt={hotel.name} />
                ) : (
                  <div className="placeholder-image">No Image</div>
                )}
              </div>
              <div className="hotel-info">
                <h2>{hotel.name}</h2>
                <p className="hotel-location">{hotel.city}</p>
                <p className="hotel-description">{hotel.description.substring(0, 100)}...</p>
                <Link to={`/hotel/${hotel.id}`} className="view-details-btn">
                  View Details
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Home;