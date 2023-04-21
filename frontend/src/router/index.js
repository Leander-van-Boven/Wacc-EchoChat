import Vue from 'vue'
import Router from 'vue-router'
import LoginView from '@/views/LoginView'
import ChatView from '@/views/ChatView'
import AdminView from '@/views/AdminView'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'root',
      component: LoginView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path:'/chat',
      name:'chat',
      component: ChatView
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView
    }
  ]
})
