<template>
  <div class="loginMain">
    <div>
      <img class="loginLogo" src="@/assets/logo.jpeg" alt="app logo"/>
      <h1>Login to start chatting!</h1>
      <div v-if="!loading">
        <p class="loginErrorDisplay">{{ loginError }}</p>
        <form action="post">
          <label><b>Username</b></label>
          <input type="text" v-model="username" required>
          <label><b>Password</b></label>
          <input type="password" v-model="password" required>
          <input type="submit" v-on:click.prevent="login">
        </form>
        <a class="newUserButton" v-on:click.prevent="newUser">Create new user</a>
      </div>
      <LoadingAnimation v-if="loading"></LoadingAnimation>
    </div>
  </div>
</template>

<script>
import LoadingAnimation from '@/components/LoadingAnimation.vue'
import { DEFAULT_USERNAME, DEFAULT_PASSWORD } from "@/util/constants"
import userFunctions from "@/functions/userFunctions";

export default {
  name: 'LoginView',
  components: {LoadingAnimation},
  data() {
    return {
      loading: false,
      username: DEFAULT_USERNAME,
      password: DEFAULT_PASSWORD,
      loginError: ''
    }
  },

  methods: {
    login() {
      if (this.username !== '' && this.password !== '') {
        // show the loading message
        this.loading = true;
        this.loginError = ''

        userFunctions
          .loginUser(this.username, this.password)
          .then(response => {
            localStorage.setItem('userId', response.userUuid)
            localStorage.setItem('jwt', response.token)

            // TODO: Open websocket with API

            this.$router.push({name: 'chat'})
          })
          .catch(error => {
            console.log('ERROR while logging in:', error)
            if (error.response) {
              console.log('Error has response:', error.response)
              if (error.response.status === 401) {
                this.loginError = 'Username or password is incorrect.'
                return
              }
            }
            this.loginError = 'Failed to login, try again later...'
          })
          .finally(() => {
            this.loading = false;
          })
      } else {
        this.loginError = 'Username and password cannot be empty.'
      }
    },

    newUser() {
      if (this.username !== '' && this.password !== '') {
        userFunctions
          .newUser(this.username, this.password)
          .then(({}) => {
            this.newUserCreated = `${this.username} successfully added, you can now use these credentials to log in.`
          })
          .catch(error => {
            if (error.response) {
              if (error.response.status === 409) {
                this.loginError = 'User already exists, please use another username.'
                return
              }
            }
            this.loginError = 'Failed to create new user, try again later...'
          })
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}

form {
  width: 90%;
  margin: auto;
  display: block;
}

label {
  display: table-row;
}

input[type=text], input[type=password] {
  width: 100%;
  display: inline-block;
  padding: 12px 20px;
  margin: 8px 0;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

input[type=submit] {
  width: 100%;
  background-color: #1061e4;
  color: white;
  padding: 14px 20px;
  margin: 8px 0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

input[type=submit]:hover {
  background-color: #0530b2;
}

.loginLogo {
  height: auto;
  width: 80%;
  margin: 1rem;
}

@media only screen and (min-width: 600px) {
  .loginLogo {
    width: 25%;
  }

  form {
    width: 35%;
  }
}

.loginErrorDisplay {
  color: firebrick;
}

.newUserButton {
  color: #1061e4;
  cursor: pointer;
}
.newUserButton:hover {
  color: #0530b2;
}

</style>
