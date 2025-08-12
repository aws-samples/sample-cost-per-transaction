/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const onCreateHotel = /* GraphQL */ `
  subscription OnCreateHotel($filter: ModelSubscriptionHotelFilterInput) {
    onCreateHotel(filter: $filter) {
      id
      name
      description
      address
      city
      imageUrl
      rooms {
        items {
          id
          hotelID
          name
          description
          price
          imageUrl
          capacity
          amenities
          isAvailable
          createdAt
          updatedAt
        }
        nextToken
      }
      createdAt
      updatedAt
    }
  }
`;
export const onUpdateHotel = /* GraphQL */ `
  subscription OnUpdateHotel($filter: ModelSubscriptionHotelFilterInput) {
    onUpdateHotel(filter: $filter) {
      id
      name
      description
      address
      city
      imageUrl
      rooms {
        items {
          id
          hotelID
          name
          description
          price
          imageUrl
          capacity
          amenities
          isAvailable
          createdAt
          updatedAt
        }
        nextToken
      }
      createdAt
      updatedAt
    }
  }
`;
export const onDeleteHotel = /* GraphQL */ `
  subscription OnDeleteHotel($filter: ModelSubscriptionHotelFilterInput) {
    onDeleteHotel(filter: $filter) {
      id
      name
      description
      address
      city
      imageUrl
      rooms {
        items {
          id
          hotelID
          name
          description
          price
          imageUrl
          capacity
          amenities
          isAvailable
          createdAt
          updatedAt
        }
        nextToken
      }
      createdAt
      updatedAt
    }
  }
`;
export const onCreateRoom = /* GraphQL */ `
  subscription OnCreateRoom($filter: ModelSubscriptionRoomFilterInput) {
    onCreateRoom(filter: $filter) {
      id
      hotelID
      name
      description
      price
      imageUrl
      capacity
      amenities
      isAvailable
      bookings {
        items {
          id
          roomID
          userID
          startDate
          endDate
          totalPrice
          status
          guestName
          guestEmail
          specialRequests
          createdAt
          updatedAt
        }
        nextToken
      }
      createdAt
      updatedAt
    }
  }
`;
export const onUpdateRoom = /* GraphQL */ `
  subscription OnUpdateRoom($filter: ModelSubscriptionRoomFilterInput) {
    onUpdateRoom(filter: $filter) {
      id
      hotelID
      name
      description
      price
      imageUrl
      capacity
      amenities
      isAvailable
      bookings {
        items {
          id
          roomID
          userID
          startDate
          endDate
          totalPrice
          status
          guestName
          guestEmail
          specialRequests
          createdAt
          updatedAt
        }
        nextToken
      }
      createdAt
      updatedAt
    }
  }
`;
export const onDeleteRoom = /* GraphQL */ `
  subscription OnDeleteRoom($filter: ModelSubscriptionRoomFilterInput) {
    onDeleteRoom(filter: $filter) {
      id
      hotelID
      name
      description
      price
      imageUrl
      capacity
      amenities
      isAvailable
      bookings {
        items {
          id
          roomID
          userID
          startDate
          endDate
          totalPrice
          status
          guestName
          guestEmail
          specialRequests
          createdAt
          updatedAt
        }
        nextToken
      }
      createdAt
      updatedAt
    }
  }
`;
export const onCreateBooking = /* GraphQL */ `
  subscription OnCreateBooking($filter: ModelSubscriptionBookingFilterInput) {
    onCreateBooking(filter: $filter) {
      id
      roomID
      userID
      startDate
      endDate
      totalPrice
      status
      guestName
      guestEmail
      specialRequests
      createdAt
      updatedAt
    }
  }
`;
export const onUpdateBooking = /* GraphQL */ `
  subscription OnUpdateBooking($filter: ModelSubscriptionBookingFilterInput) {
    onUpdateBooking(filter: $filter) {
      id
      roomID
      userID
      startDate
      endDate
      totalPrice
      status
      guestName
      guestEmail
      specialRequests
      createdAt
      updatedAt
    }
  }
`;
export const onDeleteBooking = /* GraphQL */ `
  subscription OnDeleteBooking($filter: ModelSubscriptionBookingFilterInput) {
    onDeleteBooking(filter: $filter) {
      id
      roomID
      userID
      startDate
      endDate
      totalPrice
      status
      guestName
      guestEmail
      specialRequests
      createdAt
      updatedAt
    }
  }
`;