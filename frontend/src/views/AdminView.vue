<template>
  <div class="mainContainer">
    <div class="login" v-if="!loggedIn">
      <div>
        <img class="logo" src="@/assets/logo.jpeg" alt="app logo" />
        <h1>Echochat Admin</h1>
        <div v-if="!loading">
          <p class="loginErrorDisplay">{{ loginError }}</p>
          <form action="post">
            <label><b>Username</b></label>
            <input type="text" v-model="username" required>
            <label><b>Password</b></label>
            <input type="password" v-model="password" required>
            <input type="submit" v-on:click.prevent="login">
          </form>
          <a class="toChatButton" v-on:click.prevent="toChat">Back to chat</a>
        </div>
        <LoadingAnimation v-if="loading"></LoadingAnimation>
      </div>
    </div>
    <div class="adminContainer" v-if="loggedIn">
      <div class="banner">
        Successfully logged in into admin page
        <button id="logout" class="logoutButton" @click="logout">
          <font-awesome-icon icon="fa-solid fa-arrow-right-from-bracket" title="Log out" />
        </button>
      </div>
      <div class="mainDiv">
        <div style="color: firebrick; font-size: 80%;">
          {{ statisticsError }}
        </div>
        <table>
          <tr>
            <th>Statistic</th>
            <th>Value</th>
          </tr>
          <tr>
            <td>Total user count</td>
            <td>{{ userCount }}</td>
          </tr>
          <tr>
            <td style="text-align: right">🟢 Online</td>
            <td>{{ onlineUsers }}</td>
          </tr>
          <tr>
            <td style="text-align: right">🔴 Offline</td>
            <td>{{ offlineUsers }}</td>
          </tr>
        </table>
        <apex-chart
          type="donut"
          height="350"
          :options="chartOptions"
          :series="chartSeries">
        </apex-chart>
      </div>
    </div>
  </div>
</template>

<script>
import LoadingAnimation from '@/components/LoadingAnimation.vue'
import { DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD } from '@/util/constants'
import userFunctions from '@/functions/userFunctions'
import websocketFunctions from '@/functions/websocketFunctions'

export default {
  name: 'AdminView',
  components: { LoadingAnimation },
  data() {
    return {
      loggedIn: false,
      loading: false,
      username: DEFAULT_ADMIN_USERNAME,
      password: DEFAULT_ADMIN_PASSWORD,
      loginError: '',

      adminUuid: '',
      statisticsError: '',

      userCount: '[pending]',
      onlineUsers: '[pending]',
      offlineUsers: '[pending]',

      chartOptions: {
        labels: ['Online', 'Offline'],
        colors: ['#00ff00', '#ff0000'],
        plotOptions: {
          pie: {
            donut: {
              labels: {
                show: true,
                name: {
                  show: true,
                  fontSize: '22px',
                  fontFamily: 'Helvetica, Arial, sans-serif',
                  fontWeight: 600,
                  color: '#fff',
                  offsetY: -10,
                },
                value: {
                  show: true,
                  fontSize: '16px',
                  fontFamily: 'Helvetica, Arial, sans-serif',
                  fontWeight: 400,
                  color: '#fff',
                  offsetY: 16,
                  formatter: function (val) {
                    return val
                  },
                },
                total: {
                  show: true,
                  label: 'Total',
                  color: '#fff',
                  formatter: function (w) {
                    return w.globals.seriesTotals.reduce((a, b) => {
                      return a + b
                    }, 0)
                  },
                },
              },
            },
          },
        },
        legend: {
          labels: {
            colors: '#fff',
          },
        },
      },
      chartSeries: [0, 0],

      socket: null,
    }
  },
  mounted() {
    if (localStorage.getItem('adminJwt')) {
      this.loggedIn = true
      this.createSocketConnection()
    }
  },

  methods: {
    login() {
      if (this.username !== '' && this.password !== '') {
        this.loading = true;
        this.loginError = ''

        userFunctions
          .loginAdminUser(this.username, this.password)
          .then(response => {
            if (!response.isAdmin) {
              throw new Error('You are not an admin.')
            }

            localStorage.setItem('adminJwt', response.token)
            localStorage.setItem('adminUuid', response.userUuid)
            this.adminUuid = response.userUuid
            this.loggedIn = true
            this.createSocketConnection()
          })
          .catch(error => {
            console.log('ERROR while logging in into admin page:', error)
            if (error.response) {
              console.log('Error has response:', error.response)
              if (error.response.status === 401) {
                this.loginError = 'Username or password is incorrect.'
                return
              }
            } else if (error.message === 'You are not an admin.') {
              this.loginError = 'You are not an admin.'
            } else {
              this.loginError = 'Failed to login, try again later...'
            }
          })
          .finally(() => {
            this.loading = false;
          })
      } else {
        this.loginError = 'Username and password cannot be empty.'
      }
    },

    handleUserStatisticsUpdate(props) {
      this.userCount = props.userCount
      this.onlineUsers = props.onlineUsers
      this.offlineUsers = this.userCount - this.onlineUsers
      this.chartSeries = [this.onlineUsers, this.offlineUsers]
    },

    handleStatisticsReceived(props) {
      const action = props.action
      switch (action) {
        case 'user_statistics_update':
          this.handleUserStatisticsUpdate(props.statistics)
          break
        case 'error':
          this.statisticsError = `Error while receiving statistics: ${props.message}`
          break
      }
    },

    handleSocketClosed() {
      console.log('Socket closed')
      this.statisticsError = 'Socket closed, please refresh page or log in again'
      this.socket = null
    },

    createSocketConnection() {
      this.socket = websocketFunctions.createWebsocket(
        this.adminUuid, {
          onMessageCallback: this.handleStatisticsReceived,
          onCloseCallback: this.handleSocketClosed,
          websocketUrlAddition: '/admin',
        }
      )
    },

    logout() {
      localStorage.removeItem('adminJwt')
      localStorage.removeItem('adminUuid')
      this.statisticsError = ''
      this.adminUuid = ''
      try {
        this.socket.close()
      } catch (error) {
        console.log('Error while closing socket:', error)
      }
      this.loggedIn = false
    },

    toChat() {
      this.$router.push({name: 'chat'})
    }
  }
}
</script>

<style scoped>
h1,
h2 {
  font-weight: normal;
}

form {
  width: 90%;
  margin: auto;
  display: block;
}

label {
  display: table-row;
}

input[type=text],
input[type=password] {
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

.logo {
  height: auto;
  width: 80%;
  margin: 1rem;
  border: 3px solid #f00;
}

@media only screen and (min-width: 600px) {
  .logo {
    width: 25%;
  }

  form {
    width: 35%;
  }
}

.loginErrorDisplay {
  color: firebrick;
}

.mainContainer {
  height: 100%;
}

.banner {
  position: fixed;
  left: 0;
  top: 0;
  width: 100%;
  background-color: red;
  color: white;
  padding: 5px;
  font-size: 90%;
}

.logoutButton {
  float: right;
  margin-left: auto;
  margin-right: 15px;
  background-color: transparent;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 100%;
  padding: 2px;
  border-radius: 3px;
  transition: all .25s;
}
.logoutButton:hover {
  color: #f00;
  background-color: #fff;
  transition: all .5s;
}

.toChatButton {
  color: #1061e4;
  cursor: pointer;
}
.toChatButton:hover {
  color: #0530b2;
}

.adminContainer {
  height: 100%;
  background: #1e1e1e;
  color: #fff;
}

.mainDiv {
  padding: 1rem;
  padding-top: 50px;
}

table {
  text-align: left;
  border-collapse: collapse;
}

th, td {
  padding: 8px;
}

th {
  border-bottom: 1px solid #777;
}

</style>
