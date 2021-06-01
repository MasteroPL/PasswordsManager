import Vue from 'vue'
import App from './App.vue'

// custom styles
import './assets/css/styles.scss'
import Vuetify from 'vuetify/lib'
import VueRouter from 'vue-router'
import router from './router'

Vue.use(Vuetify);
Vue.use(VueRouter);

//
// Custom components section
//
import ShareDialog from './components/common/dialogs/ShareDialog.vue'
import NewPasswordDialog from './components/common/dialogs/NewPasswordDialog.vue'
import EditShareDialog from './components/common/dialogs/EditShareDialog.vue'
import EditPasswordDialog from './components/common/dialogs/EditPasswordDialog'
import DeletePasswordDialog from './components/common/dialogs/DeletePasswordDialog.vue'
import RemoveMyPasswordAssignmentDialog from './components/common/dialogs/RemoveMyPasswordAssignmentDialog.vue'
import ChangePasswordOwnerDialog from './components/common/dialogs/ChangePasswordOwnerDialog.vue'

Vue.component('share-dialog', ShareDialog);
Vue.component('new-password-dialog', NewPasswordDialog);
Vue.component('edit-share-dialog', EditShareDialog);
Vue.component('edit-password-dialog', EditPasswordDialog);
Vue.component('delete-password-dialog', DeletePasswordDialog);
Vue.component('remove-my-password-assignment-dialog', RemoveMyPasswordAssignmentDialog);
Vue.component('change-password-owner-dialog', ChangePasswordOwnerDialog);

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
  render: h => h(App)
}).$mount('#app')

