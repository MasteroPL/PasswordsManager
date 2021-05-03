import VueRouter from 'vue-router'
import Dev from './components/Dev.vue'
import HelloWorld from './components/HelloWorld.vue'
import PasswordsList from './components/PasswordsList.vue'
import Login from './components/Login.vue'

const router = new VueRouter({
    routes: [
        {path: '/dev/', component: Dev},
        {path: '/', component: HelloWorld },
        {path: '/passwords-list/', component: PasswordsList},
        {path: '/login/', component: Login},
    ]
});

export default router;