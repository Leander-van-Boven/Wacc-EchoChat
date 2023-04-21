import {API_URL, DEFAULT_MESSAGE_FETCH_COUNT} from "@/util/constants"
import axios from "axios"
import {authConfig} from "@/util/axiosConfig"
import handleAxiosError from "./errorFunctions"

const baseUrl = `${API_URL}/room`

/**
 * A collection of functions that interact with the backend API to perform CRUD operations on rooms.
 */
const messageFunctions = {
  /**
   * Fetches messages for a chatroom
   * @param {Object} {roomId: String} The id of the room to fetch messages for 
   * @param {String} pagingState      Paging state to use for fetching messages
   * @returns {Promise}               A promise that resolves to an array of message objects
   */
  fetchMessages({roomId}, pagingState = null) {
    let url = `${baseUrl}/${roomId}/message?c=${DEFAULT_MESSAGE_FETCH_COUNT}`
    if (pagingState) {
      url += `&ps=${pagingState}`
    }

    return axios
      .get(url, authConfig())
      .then(response => response.data)
      .catch(error => {
        handleAxiosError(error, 'ERROR while fetching messages')
        return []
      })
  },

  /**
   * Sends a message to a chatroom
   * @param {WebSocket} socket           The websocket connection to the backend
   * @param {Object} param2
   * @param {String} param2.userId       The id of the user sending the message
   * @param {String} param2.roomId       The id of the room to send the message to
   * @param {String} param2.content      The text of the message to send
   * @param {String} param2.replyMessage An optional message to reply to
   * @param {String} param2.usersTag     An optional list of users to tag [TODO: Implement]
   */
  sendMessage(socket, {userId, roomId, content, replyMessage, usersTag}) {
    return new Promise((resolve) => {
      const message = {
        type: 'send',
        topic: 'new_message',
        data: {
          userId: userId,
          roomId: roomId,
          content: content,
          replyMessage: replyMessage
        }
      }

      socket.send(JSON.stringify(message))
      resolve()
    })
  },

  /**
   * Updates the message seen status of a message
   * @param {WebSocket} socket    The websocket connection to the backend
   * @param {String} roomId       The id of the room in which the message resides
   * @param {String} messageIndex The index of the message to update (datetime)
   * @param {String} messageId    The id of the message to update
   */
  sendMessageSeen(socket, roomId, messageIndex, messageId) {
    return new Promise((resolve) => {
      const message = {
        type: 'send',
        topic: 'message_seen',
        data: {
          roomId: roomId,
          messageIndex: messageIndex,
          messageId: messageId
        }
      }

      socket.send(JSON.stringify(message))
      resolve()
    })
  }
}

export default messageFunctions

// MESSAGES PROP
// messages="[
//   {
//     _id: '7890',
//     indexId: 12092,
//     content: 'Message 1',
//     senderId: '1234',
//     username: 'John Doe',
//     avatar: 'assets/imgs/doe.png',
//     date: '13 November',
//     timestamp: '10:20',
//     system: false,
//     saved: true,
//     distributed: true,
//     seen: true,
//     deleted: false,
//     failure: true,
//     disableActions: false,
//     disableReactions: false,
//     files: [
//       {
//         name: 'My File',
//         size: 67351,
//         type: 'png',
//         audio: true,
//         duration: 14.4,
//         url: 'https://firebasestorage.googleapis.com/...',
//         preview: 'data:image/png;base64,iVBORw0KGgoAA...',
//         progress: 88
//       }
//     ],
//     reactions: {
//       😁: [
//         '1234', // USER_ID
//         '4321'
//       ],
//       🥰: [
//         '1234'
//       ]
//     },
//     replyMessage: {
//       content: 'Reply Message',
//       senderId: '4321',
//       files: [
//         {
//           name: 'My Replied File',
//           size: 67351,
//           type: 'png',
//           audio: true,
//           duration: 14.4,
//           url: 'https://firebasestorage.googleapis.com/...',
//           preview: 'data:image/png;base64,iVBORw0KGgoAA...'
//         }
//       ]
//     },
//   }
// ]"
