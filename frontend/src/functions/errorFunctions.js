
/**
 * 
 * @param {Error}  error   The error object to handle
 * @param {String} message Error message to display instead of error.message
 * @returns {null} if the error was handled, otherwise resaises the error
 */
export default function handleAxiosError(error, message = null) {
    // Sendto login to efresh JWT when it has expired
    if (error.response) {
        if (error.status === 401) {
            this.$router.push({name: 'login'})
            return;
        }
    }

    console.log(message ?? 'ERROR while handling Axios response', error)

    // Rethrow error if its a different error
    if (message) {
        error.message = message
    }
    throw error
}
