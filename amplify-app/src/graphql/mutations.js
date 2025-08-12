/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const createHotel = /* GraphQL */ `
  mutation CreateHotel(
    $input: CreateHotelInput!
    $condition: ModelHotelConditionInput
  ) {
    createHotel(input: $input, condition: $condition) {
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
export const updateHotel = /* GraphQL */ `
  mutation UpdateHotel(
    $input: UpdateHotelInput!
    $condition: ModelHotelConditionInput
  ) {
    updateHotel(input: $input, condition: $condition) {
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
export const deleteHotel = /* GraphQL */ `
  mutation DeleteHotel(
    $input: DeleteHotelInput!
    $condition: ModelHotelConditionInput
  ) {
    deleteHotel(input: $input, condition: $condition) {
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
export const createRoom = /* GraphQL */ `
  mutation CreateRoom(
    $input: CreateRoomInput!
    $condition: ModelRoomConditionInput
  ) {
    createRoom(input: $input, condition: $condition) {
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
export const updateRoom = /* GraphQL */ `
  mutation UpdateRoom(
    $input: UpdateRoomInput!
    $condition: ModelRoomConditionInput
  ) {
    updateRoom(input: $input, condition: $condition) {
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
export const deleteRoom = /* GraphQL */ `
  mutation DeleteRoom(
    $input: DeleteRoomInput!
    $condition: ModelRoomConditionInput
  ) {
    deleteRoom(input: $input, condition: $condition) {
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
export const createBooking = /* GraphQL */ `
  mutation CreateBooking(
    $input: CreateBookingInput!
    $condition: ModelBookingConditionInput
  ) {
    createBooking(input: $input, condition: $condition) {
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
export const updateBooking = /* GraphQL */ `
  mutation UpdateBooking(
    $input: UpdateBookingInput!
    $condition: ModelBookingConditionInput
  ) {
    updateBooking(input: $input, condition: $condition) {
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
export const deleteBooking = /* GraphQL */ `
  mutation DeleteBooking(
    $input: DeleteBookingInput!
    $condition: ModelBookingConditionInput
  ) {
    deleteBooking(input: $input, condition: $condition) {
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