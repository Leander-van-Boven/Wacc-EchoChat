/**
 * Bearer authentication header injection with JWT token
 * @returns {Object} The header object to be used in axios requests
 */
export function authConfig() {
  return {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("jwt")}`,
    }
  }
}

/**
 * Bearer authentication header injection with JWT admin token
 * @returns {Object} The header object to be used in axios admin requests
 */
export function adminAuthConfig() {
  return {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("adminJwt")}`,
    }
  }
}
