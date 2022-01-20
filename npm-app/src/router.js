import VueRouter from 'vue-router'
import Dev from './components/Dev.vue'
import BoardsList from './components/BoardsList.vue'
import BoardAdd from './components/BoardAdd.vue'
import Login from './components/Login.vue'
import Board from './components/Board.vue'
import BoardAdmin from './components/BoardAdmin.vue'
import BoardTabsEdit from './components/BoardTabsEdit.vue'
import BoardPasswordEdit from './components/BoardPasswordEdit.vue'

import UserPasswords from './components/UserPasswords.vue'
import UserPasswordEdit from './components/UserPasswordEdit.vue'
import UserPasswordShares from './components/UserPasswordShares.vue'
import UserPasswordsTabsEdit from './components/UserPasswordsTabsEdit.vue'

const router = new VueRouter({
    routes: [
        {path: '/dev/', component: Dev},
        {path: '/', component: Login, name:"default" },
        {path: '/boards/', component: BoardsList, name:"boards"},
        {path: '/boards/new/', component: BoardAdd, name:"boards_new"},
        {path: '/login/', component: Login, name:"login"},
        {path: '/board/:board_id/', component: Board, name:"board"},
        {path: '/board/:board_id/admin/', component: BoardAdmin, name:"board_admin"},
        {path: '/board/:board_id/tabs/', component: BoardTabsEdit, name:"board_tabs"},
        {path: '/board/:board_id/password/:password_id?', component: BoardPasswordEdit, name:"board_password_edit"},

        {path: '/user-passwords/', component: UserPasswords, name:"user_passwords"},
        {path: '/user-password/:password_id?', component: UserPasswordEdit, name:"user_password_edit"},
        {path: '/user-password/:password_id/shares/', component: UserPasswordShares},
        {path: '/user-passwords/tabs/', component: UserPasswordsTabsEdit}
    ]
});

export default router;