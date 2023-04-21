import { WEBSOCKET_URL } from "@/util/constants"

/**
 * A collection of functions to work with websocket connections to the backend.
 */
const websocketFunctions = {
  /**
   * Creates a new websocket connection to the backend.
   * @param {String} connectionId The id of the connection to create
   * @param {Object} callbacks    The callbacks to use for the connection
   * @returns 
   */
  createWebsocket(connectionId, {onOpenCallback=null, onMessageCallback, onCloseCallback, onErrorCallback=null, websocketUrlAddition=null}) {
    const websocketUrl = `${WEBSOCKET_URL}${websocketUrlAddition ? websocketUrlAddition : ''}`
    const websocket = new WebSocket(`${websocketUrl}/${connectionId}`)
    websocket.onopen = () => {
      console.log("Websocket connection established")
      if (onOpenCallback) {
        onOpenCallback(websocket)
      }
    }
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log("Websocket message received: ", data)
      onMessageCallback(data.data)
    }
    websocket.onclose = () => {
      console.log("Websocket connection closed")
      onCloseCallback()
    }
    websocket.onerror = (error) => {
      console.log("Websocket error: ", error)
      if (onErrorCallback) {
        onErrorCallback()
      }
    }
    return websocket
  },

  /**
   * Checks if a websocket connection is open, otherwise creates one.
   * @param {WebSocket}         socket            The websocket connection to check
   * @param {String}            userId            The id of the user to create a connection for
   * @param {onMessageCallback} onMessageCallback The callback to use to create a new websocket connection
   * @param {onCloseCallback}   onCloseCallback   The callback to use to create a new websocket connection
   * @returns {WebSocket}                         The websocket connection, either the one passed in or a new one
   */
  checkSocketConnection(socket, userId, onMessageCallback, onCloseCallback) {
    return new Promise((resolve, reject) => {
      if (socket.readyState === WebSocket.OPEN || socket.readyState === 1) {
        resolve(socket)
      } else {
        console.log("Websocket connection not established, creating new connection")
        this.createWebsocket(
          userId, {
          onOpenCallback: resolve,
          onMessageCallback: onMessageCallback, 
          onCloseCallback: onCloseCallback,
          onErrorCallback: reject
        })
      }
    })
  }
}

export default websocketFunctions
