/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const getHotel = /* GraphQL */ `
  query GetHotel($id: ID!) {
    getHotel(id: $id) {
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
export const listHotels = /* GraphQL */ `
  query ListHotels(
    $filter: ModelHotelFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listHotels(filter: $filter, limit: $limit, nextToken: $nextToken) {
      items {
        id
        name
        description
        address
        city
        imageUrl
        rooms {
          nextToken
        }
        createdAt
        updatedAt
      }
      nextToken
    }
  }
`;
export const getRoom = /* GraphQL */ `
  query GetRoom($id: ID!) {
    getRoom(id: $id) {
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
export const listRooms = /* GraphQL */ `
  query ListRooms(
    $filter: ModelRoomFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listRooms(filter: $filter, limit: $limit, nextToken: $nextToken) {
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
        bookings {
          nextToken
        }
        createdAt
        updatedAt
      }
      nextToken
    }
  }
`;
export const getBooking = /* GraphQL */ `
  query GetBooking($id: ID!) {
    getBooking(id: $id) {
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
export const listBookings = /* GraphQL */ `
  query ListBookings(
    $filter: ModelBookingFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listBookings(filter: $filter, limit: $limit, nextToken: $nextToken) {
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
  }
`;
export const roomsByHotelID = /* GraphQL */ `
  query RoomsByHotelID(
    $hotelID: ID!
    $sortDirection: ModelSortDirection
    $filter: ModelRoomFilterInput
    $limit: Int
    $nextToken: String
  ) {
    roomsByHotelID(
      hotelID: $hotelID
      sortDirection: $sortDirection
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
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
        bookings {
          nextToken
        }
        createdAt
        updatedAt
      }
      nextToken
    }
  }
`;
export const bookingsByRoomID = /* GraphQL */ `
  query BookingsByRoomID(
    $roomID: ID!
    $sortDirection: ModelSortDirection
    $filter: ModelBookingFilterInput
    $limit: Int
    $nextToken: String
  ) {
    bookingsByRoomID(
      roomID: $roomID
      sortDirection: $sortDirection
      filter: $filter
      limit: $limit
      nextToken: $nextToken
    ) {
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
  }
`;