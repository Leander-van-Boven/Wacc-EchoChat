import {API_URL} from "@/util/constants"
import axios from "axios"
import {authConfig} from "@/util/axiosConfig"
import handleAxiosError from "./errorFunctions"

const baseUrl = `${API_URL}/search`

/**
 * A collection of functions that interact with the backend API to perform search queries.
 */
const searchFunctions = {
  /**
   * Searches for messages by content
   * @param {String} searchQuery The content to search for within messages
   * @returns {Promise}          A promise that resolves to an array of message objects
   */
  searchMessagesByContent(searchQuery) {
    return axios
      .get(`${baseUrl}/messages/content?c=${searchQuery}`, authConfig())
      .then(response => response.data)
      .catch(error => {
        handleAxiosError(error, 'ERROR while searching messages by content:')
        return {}
      })
  },

  /**
   * Searches for chatrooms by room name (only within the user's chatrooms)
   * @param {String} searchQuery The room name to search for
   * @returns {Promise}          A promise that resolves to an array of room objects
   */
  searchRoomsByName(searchQuery) {
    return axios
      .get(`${baseUrl}/rooms/name?n=${searchQuery}`, authConfig())
      .then(response => response.data)
      .catch(error => {
        handleAxiosError(error, 'ERROR while searching rooms by name:')
        return {}
      })
  }
}

export default searchFunctions
