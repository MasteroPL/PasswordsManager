import VueRouter from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import PasswordsList from './components/PasswordsList.vue'

const router = new VueRouter({
    routes: [
        {path: '/', component: HelloWorld },
        {path: '/passwords-list/', component: PasswordsList}
    ]
});

export default router;