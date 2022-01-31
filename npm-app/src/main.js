import Vue from 'vue'
import App from './App.vue'
import 'material-design-icons-iconfont/dist/material-design-icons.css'

// custom styles
import './assets/css/styles.scss'
import Vuetify from 'vuetify/lib'
import VueRouter from 'vue-router'
import router from './router'
import store from './store/index.js'

Vue.use(Vuetify);
Vue.use(VueRouter);


// Credits to LinusBorg: https://forum.vuejs.org/t/conditionally-render-parent-element/9324
Vue.component('with-root', {
  functional: true,
  props: ['show'],
  render(h, ctx) {
    const children = ctx.children.filter(vnode => vnode.tag) // remove unnecessary text nodes
    if (children.length !== 1) {
      console.warn('this component accepts only one root node in its slot')
    }
    if (ctx.props.show) {
      return children[0]
    } else {
      return children[0].children
    }
  }
});
//
// End of Custom components section
//

const vuetify = new Vuetify({
  theme: {
    options: { customProperties: true },
    //disable: true,
    themes: {
      light: {
        primary: "#1976d2",
        secondary: "#eeb006",
        accent: "#03a9f4",
        error: "#f44336",
        warning: "#ff9800",
        info: "#00bcd4",
        success: "#4caf50"
      },
      dark: {
        primary: "#2676d1",
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
  store,
  render: h => h(App)
}).$mount('#app')

