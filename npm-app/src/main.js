import Vue from 'vue'
import App from './App.vue'

// custom styles
import './assets/css/styles.scss'
import Vuetify from 'vuetify/lib'
import VueRouter from 'vue-router'
import router from './router'

Vue.use(Vuetify);
Vue.use(VueRouter);

const vuetify = new Vuetify({
  theme: {
    options: { customProperties: true },
    //disable: true,
    themes: {
      light: {
        primary: "#1976d2",
        secondary: "#ffc107",
        accent: "#03a9f4",
        error: "#f44336",
        warning: "#ff9800",
        info: "#00bcd4",
        success: "#4caf50"
      },
      dark: {
        primary: "#1565c0",
        secondary: "#ffc107",
        accent: "#03a9f4",
        error: "#f44336",
        warning: "#ff9800",
        info: "#00bcd4",
        success: "#4caf50"
      }
    }
  }
});

Vue.config.productionTip = false

new Vue({
  vuetify,
  router,
  render: h => h(App)
}).$mount('#app')

