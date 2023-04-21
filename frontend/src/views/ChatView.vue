<template>
  <div :style="cssVars" class="chatContainer">
    <vue-advanced-chat height="100%" width="100%" :current-user-id="currentUserId" :rooms="JSON.stringify(rooms)"
      rooms-order="desc" :loading-rooms="roomsLoading" :rooms-loaded="roomsLoaded" :messages="JSON.stringify(messages)"
      :messages-loaded="messagesLoaded" show-search="true" show-add-room="false" show-files="false" show-audio="false" show-emojis="true"
      show-reaction-emojis="false" show-new-messages-divider="false" scroll-distance="60" :theme="theme"
      :room-actions="JSON.stringify(roomActions)" @room-action-handler="roomActionHandler($event.detail[0])"
      @fetch-more-rooms="fetchMoreRooms()" @fetch-messages="fetchMessages($event.detail[0])"
      @send-message="sendMessage($event.detail[0])">
      <div slot="rooms-header">
        <div class="roomsHeader">
          <div class="headerContainer">
            <div class="logoContainer">
              <img src="@/assets/logo.jpeg" class="logo" alt="app logo" />
              <h3 class="logoName">Echo Chat</h3>
            </div>
            <div class="buttonContainer">
              <button id="toggleJoinRoom" class="iconBtn" @click="toggleJoinRoom">
                <font-awesome-icon icon="fa-regular fa-square-plus" title="Add or join chatroom"/>
              </button>
              <button id="logout" class="iconBtn" @click="logout">
                <font-awesome-icon icon="fa-solid fa-arrow-right-from-bracket" title="Log out" />
              </button>
              <button id="theme-button" class="themeButton" @click="toggleTheme">
                <font-awesome-icon :icon="themeIcon" title="Change theme" />
              </button>
            </div>
          </div>
          <div class="loggedUserContainer">
              <div>Welcome! You are logged in as:</div>
              <div class="currentUser">{{ currentUserId }}</div>
            </div>
        </div>
      </div>
      <div slot="rooms-list-search">
        <div class="searchDiv" v-if="!joinRoom">
          <font-awesome-icon icon="fa-solid fa-search" class="searchIcon"/>
          <input class="searchBox" type="search" v-model="searchMessagesQuery" autocorrect="off" placeholder="Search for messages" @input="searchMessages" />
        </div>
        <div v-if="joinRoom">
          <div class="joinRoomErr">
            {{ joinRoomError }}
          </div>
          <div class="joinRoomOptions">
            <label class="customRadioLabel">Join room
              <input type="radio" value="joinRoom" v-model="joinRoomType" />
              <span class="checkmark"></span>
            </label>
            <label class="customRadioLabel">Create new room
              <input type="radio" value="createRoom" v-model="joinRoomType" />
              <span class="checkmark"></span>
            </label>
          </div>

          <div class="searchDiv">
            <input class="searchBox" style="padding: 10px;" type="search" v-model="joinRoomQuery" autocorrect="off" :placeholder="joinRoomPlaceholder"/>
          </div>
          <div class="joinRoomDiv">
            <button class="joinRoomBtn" @click="joinRoomBtnClick">
              <font-awesome-icon :icon="joinRoomIcon" class="joinRoomIcn"/>
              <div class="joinRoomBtnTxt">{{ joinRoomBtnTxt }}</div>
            </button>
            <button class="cancelJoinRoomBtn" @click="cancelJoinRoom">
              <font-awesome-icon icon="fa-solid fa-xmark" class="cancelJoinRoomIcn"/>
              <div class="cancelJoinRoomBtnTxt">Cancel</div>
            </button>
          </div>
        </div>
      </div>
      <div slot="no-room-selected" v-if="fetchRoomError" 
           style="width:100%; height:100%; text-align:center; display:flex; justify-content: center; flex-direction: column; color:firebrick">
          Failed to fetch rooms. Please try again later.
      </div>
    </vue-advanced-chat>
  </div>
</template>

<script>
import { register } from 'vue-advanced-chat'
import roomFunctions from '@/functions/roomFunctions'
import { faLightbulb, } from "@fortawesome/free-regular-svg-icons"
import { faLightbulb as faLightbulbSolid, faPlus, faArrowRightToBracket } from "@fortawesome/free-solid-svg-icons"
import messageFunctions from "@/functions/messageFunctions"
import userFunctions from "@/functions/userFunctions"
import websocketFunctions from "@/functions/websocketFunctions"
import searchFunctions from "@/functions/searchFunctions"
// import { register } from '../../vue-advanced-chat/dist/vue-advanced-chat.es.js'
register()

export default {
  name: 'ChatView',
  data() {
    return {
      currentUserId: '',
      socket: null,

      rooms: [],
      roomsLoading: false,
      roomsLoaded: false,
      activeRoomId: null,
      fetchRoomError: false,

      joinRoom: false,
      joinRoomType: 'joinRoom',
      joinRoomIcon: faArrowRightToBracket,
      joinRoomPlaceholder: 'Enter room name',
      joinRoomBtnTxt: 'Try to join room',
      joinRoomQuery: '',
      joinRoomError: '',

      roomActions: [
        { name: 'leaveChatRoom', title: 'Leave chatroom' }
      ],

      messages: [],
      messagesLoaded: false,
      pagingState: null,

      searchMessagesQuery: '',

      theme: 'light'
    }
  },

  watch: {
    joinRoomType(newValue) {
      this.joinRoomQuery = ''
      this.joinRoomError = ''
      if (newValue === 'joinRoom') {
        this.joinRoomIcon = faArrowRightToBracket
        this.joinRoomBtnTxt = 'Try to join room'
        this.joinRoomPlaceholder = 'Enter room name'
      } else if (newValue === 'createRoom') {
        this.joinRoomIcon = faPlus
        this.joinRoomBtnTxt = 'Create new room'
        this.joinRoomPlaceholder = 'Enter new room name'
      }
    }
  },

  methods: {
    // ROOMS
    toggleJoinRoom() {
      this.joinRoom = !this.joinRoom
      if (!this.joinRoom) {
        this.joinRoomQuery = ''
        this.joinRoomError = ''
      }
    },

    cancelJoinRoom() {
      this.joinRoom = false
      this.joinRoomQuery = ''
      this.joinRoomError = ''
    },

    joinRoomBtnClick() {
      this.joinRoomError = ''
      if (this.joinRoomQuery.length > 0) {
        if (this.joinRoomType === 'joinRoom') {
          roomFunctions
            .joinRoom(this.joinRoomQuery)
            .then(newRoom => {
              if (newRoom === null) {
                return
              }
              this.rooms = [...this.rooms, newRoom]
              this.joinRoomQuery = ''
            })
            .catch(err => {
              this.joinRoomError = err
            })
        } else if (this.joinRoomType === 'createRoom') {
          roomFunctions
            .createRoom(this.joinRoomQuery)
            .then(newRoom => {
              if (newRoom === null) {
                return
              }
              this.rooms = [...this.rooms, newRoom]
              this.joinRoomQuery = ''
            })
            .catch(err => {
              this.joinRoomError = err
            })
        }
      } else {
        this.joinRoomError = 'Please enter a chatroom- or username'
      }
    },

    fetchMoreRooms(reset = false) {
      this.roomsLoading = true
      this.fetchRoomError = false
      roomFunctions
        .fetchMoreRooms()
        .then(rooms => {
          if (reset) {
            this.rooms = rooms
            this.activeRoomId = rooms[0].index
          } else {
            this.rooms = [...this.rooms, ...rooms]
          }
        })
        .catch(error => {
          console.log('ERROR while fetching more rooms:', error)
          this.fetchRoomError = true
          this.rooms = []
        })
        .finally(() => {
          this.roomsLoading = false
          this.roomsLoaded = true
        })
    },
    
    roomActionHandler({action, roomId}) {
      if (action.name === 'leaveChatRoom') {
        roomFunctions
          .leaveRoom(roomId)
          .then(success => {
            if (success) {
              this.rooms = this.rooms.filter(room => room.roomId !== roomId)
            }
          })
      }
    },

    // MESSAGES
    showErrorMessage(message, error, reset) {
      let content = message ? message : (error ? error.message : 'Something went wrong')
      if (message && error) {
        content = `${content}: ${error.message}`
      }
      console.log(content)
      const errorMessage = {
        _id: -1,
        content: `${content}, please try again later`,
        system: true,
        senderId: -1,
        date: this.formatDate(new Date, [{day: 'numeric'}, {month: 'numeric'}, {year: 'numeric'}], '-')
      }

      if (reset) {
        this.messages = [errorMessage]
      } else {
        this.messages = [...this.messages, errorMessage]
      }
    },

    showWebsocketClosedMessage() {
      this.messages = [...this.messages, {
        _id: -1,
        content: 'Websocket connection closed, please refresh the page',
        system: true,
        senderId: -1,
        date: this.formatDate(new Date, [{day: 'numeric'}, {month: 'numeric'}, {year: 'numeric'}], '-')
      }]
    },

    fetchMessages({ room, options = {} }) {
      this.activeRoomId = room.roomId
      this.messagesLoaded = false
      if (options.reset) {
        messageFunctions
          .fetchMessages(room)
          .then(response => {
            this.pagingState = response.pagingState
            this.messagesLoaded = response.pagingState === null ? true : false
            this.messages = response.messages.reverse()
          })
          .catch(error => {
            this.showErrorMessage('', error, true)
            this.messagesLoaded = true
          })
      } else {
        messageFunctions
          .fetchMessages(room, this.pagingState)
          .then(response => {
            this.pagingState = response.pagingState
            this.messagesLoaded = response.pagingState === null ? true : false
            this.messages = [...response.messages.reverse(), ...this.messages]
          })
          .catch(error => {
            this.showErrorMessage(error)
            this.messagesLoaded = true
          })
      }
    },
    sendMessage(props) {
      props.userId = this.currentUserId
      websocketFunctions
        .checkSocketConnection(
          this.socket, 
          this.currentUserId, 
          this.messageReceived, 
          this.showWebsocketClosedMessage
        )
        .then(socket => {
          if (socket !== this.socket) {
            this.socket = socket
          }
          messageFunctions.sendMessage(this.socket, props)
        })
        .catch(error => this.showErrorMessage('ERROR while trying to send message', error, false))
    },

    handleNewMessage(props) {
      const roomId = props.roomId
      const message = props.message

      this.rooms.find(room => room.roomId === roomId).lastMessage = message
      this.rooms = [...this.rooms]
      
      if (roomId === this.activeRoomId) {
        // Only add the message if it is in the currently selected room
        this.messages = [...this.messages, message]

        if (message.senderId !== this.currentUserId) {
          messageFunctions.sendMessageSeen(this.socket, roomId, message.indexId, message._id)
        }
      }

      if (message.senderId !== this.currentUserId) {
        // Send browser notification
        this.$notification.show(`New message from ${message.username} in ${this.rooms.find(room => room.roomId === roomId).roomName}`, { body: message.content }, {})
      }
    },
    
    handleMessageUpdate(props) {
      const roomId = props.roomId
      const messageId = props.messageId
      if (roomId === this.activeRoomId) {
        const messageIndex = this.messages.findIndex(message => message._id === messageId)
        this.messages[messageIndex] = {
          ...this.messages[messageIndex],
          ...props.props
        } 
        this.messages = [...this.messages]
      } else {
        const roomIndex = this.rooms.findIndex(room => room.roomId === roomId)
        if (this.rooms[roomIndex].lastMessage._id === messageId) {
          this.rooms[roomIndex].lastMessage = {
            ...this.rooms[roomIndex].lastMessage,
            ...props.props
          }
          this.rooms = [...this.rooms]
        }
      }
    },

    handleUserUpdate(props) {
      const userId = props.userId
      this.rooms.forEach(room => {
        if (room.users.find(user => user._id === userId)) {
          room.users = room.users.map(user => {
            if (user._id === userId) {
              return {
                ...user,
                ...props.props
              }
            } else {
              return user
            }
          })
        }
      })
    },

    messageReceived(props) {
      const action = props.action
      switch (action) {
        case 'new_message':
          this.handleNewMessage(props)
          break
        case 'message_update':
          this.handleMessageUpdate(props)
          break
        case 'user_update':
          this.handleUserUpdate(props)
          break
        case 'error':
          this.showErrorMessage('ERROR on websocket', props.message, false)
          break
      }
    },

    searchMessages() {
      if (this.searchMessagesQuery.length === 0) {
        this.fetchMoreRooms(true)
        this.fetchMessages({ room: this.rooms[0], options: { reset: true } })

      } else if (this.searchMessagesQuery.length > 2) {  // Imitate Whatsaap's search behaviour (starts only searching for message content from 3+ characters)
        searchFunctions
          .searchMessagesByContent(this.searchMessagesQuery)
          .then(response => {
            const total = response.total
            if (total === 0) {
              this.messages = [{
                _id: 0,
                content: 'No messages found',
                system: true,
                senderId: this.currentUserId
              }]
              return
            }

            const results = response.results
            for (var roomIndex in results) {
              if (roomIndex === this.rooms[0].roomId) {
                continue
              }
              this.rooms[roomIndex].lastMessage = results[roomIndex][0]
            }
            this.rooms[0].lastMessage = results[this.rooms[0].roomId].at(-1)
            this.rooms = [...this.rooms]

            this.messages = results[this.rooms[0].roomId]
          })
          .finally(() => {
            this.messagesLoaded = true
          })

      } else {  // Imitate Whatsaap's search behaviour (search within rooms/contacts from 1-2 characters)
        searchFunctions
          .searchRoomsByName(this.searchMessagesQuery)
          .then(response => {
            const total = response.total
            if (total === 0) {
              return
            }

            const results = response.results
            this.rooms = results
          })
      }
    },

    // OTHER
    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light'
      localStorage.theme = this.theme
    },

    formatDate(t, a, s) {
      const format = m => {
        let f = new Intl.DateTimeFormat('en', m);
        return f.format(t);
      }
      return a.map(format).join(s)
    },

    logout() {
      userFunctions
        .logoutUser()
        .catch(error => {
          console.log('ERROR while trying to logout, will logout anyways.', error)
        })
        .finally(() => {
          try {
            console.log('Closing socket...')
            this.socket.close()
          } catch (error) {
            console.log('ERROR while trying to close socket, will close anyways.', error)
          } finally {
            this.socket = null
          }
          localStorage.setItem('jwt', '')
          localStorage.setItem('userId', '')
          this.$router.push({ name: 'login' })
        })
    }
  },

  mounted() {
    if (!localStorage.getItem('jwt')) {
      this.$router.push({ name: 'login' })
    }

    this.currentUserId = localStorage.getItem('userId')

    // Open websocket connection to backend
    this.socket = websocketFunctions.createWebsocket(
      this.currentUserId, {
      onMessageCallback: this.messageReceived,
      onCloseCallback: this.showWebsocketClosedMessage
    })

    if (localStorage.theme) {
      this.theme = localStorage.theme
    }

    this.fetchMoreRooms()
  },

  computed: {
    cssVars() {
      return this.theme === 'dark' ? {
        '--bg-color': '#1e1e1e',
        '--text-color': '#fff',
      } : {
        '--bg-color': '#fff',
        '--text-color': '#000',
      }
    },

    themeIcon() {
      return this.theme === 'dark' ? faLightbulb : faLightbulbSolid
    }
  }
}
</script>

<style lang="scss">
.chatContainer {
  height: 100%;
  width: 100%;
  background-color: var(--bg-color);
}

.roomsHeader {
  display: table;
  width: 100%;
}

.headerContainer {
  display: flex;
  align-items: center;
  padding: 2px;
}

.logoContainer {
  display: flex;
  align-items: center;
}

.logoName {
  margin-left: 10px;
  color: var(--text-color);
}

.logo {
  width: 2.5rem;
  height: 2.5rem;
  margin-left: 10px;
}

.buttonContainer {
  margin-left: auto;
}

@media screen and (max-width: 1200px) {
  .headerContainer {
    flex-direction: column;
    align-items: flex-start;
  }
  .buttonContainer {
    margin-left: 10px;
  }

  .joinRoomOptions {
    flex-direction: column;
  }

  .joinRoomDiv {
    flex-direction: column;
  }
}

.loggedUserContainer {
  display: table;
  text-align: left;
  padding: .75rem;
}

.currentUser {
  font-style: italic;
  font-size: 75%;
  padding: 5px;
}

.themeButton {
  background: none;
  border: none;
  color: var(--text-color);
  margin-right: 10px;
  font-size: 1.5rem;
  transition: all .25s;
}

.themeButton:hover {
  cursor: pointer;
  color: #ffcc00;
  transition: .5s;
}

.iconBtn {
  background: none;
  border: none;
  color: var(--text-color);
  font-size: 1.5rem;
  transition: all .25s;
}
.iconBtn:hover {
  cursor: pointer;
  color: #1976d2;
  transition: .5s;
}

.searchDiv {
  position: sticky;
  display: flex;
  align-items: center;
  padding: 5px 15px 15px 15px;
}
.searchIcon {
  display: flex;
  position: absolute;
  left: 30px;
}
.searchBox {
  height: 38px;
  width: 100%;
  background: var(--chat-bg-color-input);
  color: var(--text-color);
  font-size: 15px;
  outline: 0;
  caret-color: #1061e4;
  padding: 10px 10px 10px 40px;
  border: 1px solid var(--chat-sidemenu-border-color-search);
  border-radius: 20px;
}

.joinRoomOptions {
  padding-left: 5px;
  display: flex;
  align-items: flex-start;
}
.joinRoomDiv {
  display: flex;
  justify-content: center;
  align-items: center;
}
.joinRoomErr {
  color: firebrick;
  font-size: 75%;
}
.joinRoomBtn {
  position: sticky;
  display: flex;
  align-items: center;
  margin: 5px 15px 15px 15px;
  border: 1px solid var(--chat-sidemenu-border-color-search);
  border-radius: 20px;
  background: #1061e4;
}
.joinRoomBtn:hover {
  cursor: pointer;
  background: #0530b2;
}
.joinRoomIcn {
  display: flex;
  position: absolute;
  left: 20px;
  color: #fff;
}
.joinRoomBtnTxt {
  width: 100%;
  color: #fff;
  font-size: 15px;
  outline: 0;
  padding: 10px 10px 10px 35px;
}
.cancelJoinRoomBtn {
  position: sticky;
  display: flex;
  align-items: center;
  margin: 5px 15px 15px 15px;
  border: 1px solid var(--chat-sidemenu-border-color-search);
  border-radius: 20px;
  background: var(--bg-color);

  &:hover {
    cursor: pointer;
    background: var(--text-color);

    .cancelJoinRoomIcn {
      color: var(--bg-color);
    }

    .cancelJoinRoomBtnTxt {
      color: var(--bg-color);
    }
  }
}
.cancelJoinRoomBtnTxt {
  width: 100%;
  color: var(--text-color);
  font-size: 15px;
  outline: 0;
  padding: 10px 10px 10px 35px;
}
.cancelJoinRoomIcn {
  display: flex;
  position: absolute;
  left: 20px;
  color: var(--text-color);
}

.customRadioLabel {
  display: block;
  position: relative;
  padding-left: 20px;
  margin: 5px;
  cursor: pointer;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
.customRadioLabel input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}
.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 16px;
  width: 16px;
  background-color: #eee;
  border-radius: 50%;
}
.customRadioLabel:hover input ~ .checkmark {
  background-color: #ccc;
}
.customRadioLabel input:checked ~ .checkmark {
  background-color: #1061e4;
}
.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}
.customRadioLabel input:checked ~ .checkmark:after {
  display: block;
}
</style>
