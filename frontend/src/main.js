import Vue from 'vue'

import {library} from '@fortawesome/fontawesome-svg-core'
import {FontAwesomeIcon} from "@fortawesome/vue-fontawesome"
import {faLightbulb, faSquarePlus} from '@fortawesome/free-regular-svg-icons'
import {faLightbulb as faLightbulbSolid, faCircleNotch, faArrowRightFromBracket, faSearch, faPlus, faArrowRightToBracket, faXmark} from '@fortawesome/free-solid-svg-icons'

import VueNativeNotification from 'vue-native-notification'
import VueApexCharts from 'vue-apexcharts'

import App from './App'
import router from "./router"
import './registerServiceWorker'

Vue.config.productionTip = false

library.add(faLightbulb, faSquarePlus)
library.add(faLightbulbSolid, faCircleNotch, faArrowRightFromBracket, faSearch, faPlus, faArrowRightToBracket, faXmark)
Vue.component('font-awesome-icon', FontAwesomeIcon)

Vue.use(VueNativeNotification, {
  requestOnNotify: true
})

Vue.use(VueApexCharts)
Vue.component('apex-chart', VueApexCharts)


new Vue({
  el: '#app',
  created:function() {
    this.checkLogin()
  },
  router,
  template: '<App/>',
  components: { App },
  methods: {
    checkLogin() {
      if (!localStorage.getItem('jwt')) {
        this.$router.push({name: 'login'}).catch(() => {})
      } else {
        this.$router.push({name: 'chat'}).catch(() => {})
      }
    }
  },
  render: h => h(App)
}).$mount('#app')
