import {API_URL} from "@/util/constants"
import axios from "axios"
import {authConfig, adminAuthConfig} from "@/util/axiosConfig";

const baseUrl = `${API_URL}/users`

/**
 * A collection of functions that interact with the backend API to perform actions on users.
 */
const userFunctions = {
  /**
   * Creates a new user
   * @param {*} username The username of the new user 
   * @param {*} password The password of the new user
   * @returns {Promise}  A promise that resolves to the new user object
   */
  newUser(username, password) {
    return axios
      .post(
        `${baseUrl}`,
        {
          username: username,
          password: password
        }
      )
      .then(response => response.data)
  },

  /**
   * Gets a user by their id
   * @param {String} userId The id of the user to get
   * @returns {Promise}     A promise that resolves to a user object
   */
  getUser(userId) {
    return axios
      .get(`${baseUrl}/${userId}`, adminAuthConfig())
      .then(response => response.data)
  },

  /**
   * Logs in a user
   * @param {String} username The username of the user to log in
   * @param {String} password The password of the user to log in
   * @returns {Promise}       A promise that resolves to a JWT token
   */
  loginUser(username, password) {
    return axios
      .post(
        `${baseUrl}/login`,
        {
          username: username,
          password: password
        }
      )
      .then(response => response.data)
  },

  /**
   * Logs in an admin user
   * @param {String} username The username of the admin user to log in
   * @param {String} password The password of the admin user to log in
   * @returns {Promise}       A promise that resolves to a JWT token
   */
  loginAdminUser(username, password) {
    return axios
      .post(
        `${baseUrl}/login/admin`,
        {
          username: username,
          password: password
        }
      )
      .then(response => response.data)
  },

  /**
   * Logs out a user
   * @returns {Promise} A promise that resolves to whether the operation was successful
   */
  logoutUser() {
    return axios
      .post(
        `${baseUrl}/logout`,
        { },
        authConfig()
      )
      .then(response => {
        if (response.status === 204) {
          return true
        } else {
          throw new Error("Error logging out")
        }
      })
  }
}

export default userFunctions
