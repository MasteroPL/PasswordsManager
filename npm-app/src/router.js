import VueRouter from 'vue-router'
import Dev from './components/Dev.vue'
import PasswordsList from './components/PasswordsList.vue'
import Login from './components/Login.vue'
import Board from './components/Board.vue'

const router = new VueRouter({
    routes: [
        {path: '/dev/', component: Dev},
        {path: '/', component: Login },
        {path: '/passwords/', component: PasswordsList},
        {path: '/login/', component: Login},
        {path: '/board/:board_id/', component: Board}
    ]
});

export default router;