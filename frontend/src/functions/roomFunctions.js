import {API_URL} from "@/util/constants"
import axios from "axios"
import {authConfig} from "@/util/axiosConfig";

const baseUrl = `${API_URL}/rooms`

/**
 * A collection of functions that interact with the backend API to perform CRUD operations on rooms.
 */
const roomFunctions = {
  /**
   * Connects the user to an existing chatroom
   * @param   {String}  roomName The name of the room to connect to
   * @returns {Promise}          A promise that resolves to the room object
   */
  joinRoom(roomName) {
    return axios
      .post(`${baseUrl}/join`, {roomName: roomName}, authConfig())
      .then(response => response.data)
  },

  /**
   * Creates a new chatroom with the user already connected to it
   * @param   {String}  newRoomName The name of the new room to create
   * @returns {Promise}             A promise that resolves to the room object
   */
  createRoom(newRoomName) {
    return axios
      .post(`${baseUrl}`, {roomName: newRoomName}, authConfig())
      .then(response => response.data)
  },

  /**
   * Disconnects a user from a chatroom
   * @param   {String}  roomId The id of the room to disconnect from
   * @returns {Promise}        A promise that resolves to whether the operation was successful
   */
  leaveRoom(roomId) {
    return axios
      .post(`${baseUrl}/${roomId}/leave`, {}, authConfig())
      .then(response => {
        if (response.status === 204) {
          return true
        } else {
          throw new Error("Error leaving room")
        }
      })
  },

  /**
   * Obtains the chatrooms the user is connected to
   * @returns {Promise} A promise that resolves to an array of room objects
   */
  fetchMoreRooms() {
    return axios
      .get(`${baseUrl}`, authConfig())
      .then(response => response.data)
  }
}

export default roomFunctions

// ROOMS PROP
// rooms="[
//   {
//     roomId: '1',
//     roomName: 'Room 1',
//     avatar: 'assets/imgs/people.png',
//     unreadCount: 4,
//     index: 3,
//     lastMessage: {
//       _id: 'xyz',
//       content: 'Last message received',
//       senderId: '1234',
//       username: 'John Doe',
//       timestamp: '10:20',
//       saved: true,
//       distributed: false,
//       seen: false,
//       new: true
//     },
//     users: [
//       {
//         _id: '1234',
//         username: 'John Doe',
//         avatar: 'assets/imgs/doe.png',
//         status: {
//           state: 'online',
//           lastChanged: 'today, 14:30'
//         }
//       },
//       {
//         _id: '4321',
//         username: 'John Snow',
//         avatar: 'assets/imgs/snow.png',
//         status: {
//           state: 'offline',
//           lastChanged: '14 July, 20:00'
//         }
//       }
//     ],
//     typingUsers: [ 4321 ]
//   }
// ]"
