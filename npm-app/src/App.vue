<template>
  <v-app class="my-app">

    <!--
      TOP BAR (visible only for mobile)
    -->
    <v-app-bar
      app
      color="primary"
      dark
      v-model="mainNavigation.mobileAppBarModel"
      scroll-target="#scrolling"

      v-if="appDisplay != 'BLANK'"
    >
      <v-app-bar-nav-icon @click="mainNavigation.model = true"></v-app-bar-nav-icon>

      <v-toolbar-title>PassManager</v-toolbar-title>
    </v-app-bar>

    <!--
      NAVIGATION
    -->
    <v-navigation-drawer 
      color="primary"
      :permanent="appMode == 'DESKTOP'"
      :temporary="appMode == 'MOBILE'" 
      class="navigation-side"
      dark
      v-model="mainNavigation.model"
      app

      v-if="appDisplay != 'BLANK'"
    >
      <!-- TOP HEADER -->
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="title">
            PassManager
          </v-list-item-title>
          <v-list-item-subtitle>
            Z nami Twoje hasła są bezpieczne
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <!-- ACCOUNT -->
      <v-list-item two-line>
        <v-list-item-avatar color="#FFFFFF" class="navbar-avatar" >
          {{ (userData != null) ? userData.initials : "##" }}
        </v-list-item-avatar>

        <v-list-item-content>
          <v-list-item-title>{{ (userData != null && userData.firstName != "") ? userData.firstName + " " : "" }}{{ (userData != null && userData.lastName != "") ? userData.lastName : "" }}</v-list-item-title>
          <v-list-item-subtitle>Zalogowany</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <!-- NAV LIST -->
      <v-list
        dense
        style="padding-top: 0"
      >
        <v-subheader>OGÓLNE</v-subheader>
        <v-list-item-group
          v-model="mainNavigation.selected"
          dark
        >
          <!-- Passwords list -->
          <v-list-item
            link
            @click="navigateTo('/passwords/')"
          >
            <v-list-item-icon>
              <v-icon>mdi-lock</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>LISTA HASEŁ</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <!-- Password boards -->
          <v-list-item
            link
            style="margin-bottom:10px"
          >
            <v-list-item-icon>
              <v-icon>mdi-view-dashboard</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>TABLICE</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-divider></v-divider>

          <v-subheader>KONTO</v-subheader>

          <!-- My profile -->
          <v-list-item
            link
          >
            <v-list-item-icon>
              <v-icon>mdi-account</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>MÓJ PROFIL</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <!-- Log out -->
          <v-list-item
            link
            @click="logout()"
          >
            <v-list-item-icon>
              <v-icon>mdi-logout</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>WYLOGUJ</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          

        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>

    <div id="scrolling">
      <v-main class="main">
        <input type="checkbox" v-model="darkMode" />
        <router-view
          :user-data="userData"
          @authorization-data-received="handleAuthorizationData"
        ></router-view>
      </v-main>
    </div>
  </v-app>
</template>

<script>

const ALLOW_UNAUTHORIZED = [
  "/",
  "/login/"
];

const DISPLAY_BLANK_URLS = [
  "/",
  "/login/"
];

import axios from 'axios'

export default {
  name: 'App',

  data: () => ({
    darkMode: false,
    mainNavigation: {
      mobileAppBarModel: false,
      model: false,
      selected: null,
      boardsOpen: false,
    },

    // Modes:
    // - DESKTOP
    // - MOBILE
    appMode: "DESKTOP",

    // Displays:
    // - DEFAULT: the regular interface after logging in
    // - BLANK: interface for pages without authorization
    appDisplay: "DEFAULT",

    boardList: [
      {
        id: 1,
        name: "Board1",
      },
      {
        id: 2,
        name: "Board2",
      }
    ],

    userData: null,
    //
  }),
  beforeMount(){
    this.loadAcessToken();
    this.loadUserData();
    this.handleRedirect();
  },
  mounted() {
    this.loadTheme();
  },

  created() {
    window.addEventListener("resize", this.handleResize);
    this.handleResize();
  },

  watch: {
    darkMode: function(){
      var htmlElement = document.documentElement;
      if(this.darkMode){
        localStorage.setItem("theme", "dark");
        htmlElement.setAttribute("theme", "dark");
        this.$vuetify.theme.dark = true;
      }
      else{
        localStorage.setItem("theme", "light");
        htmlElement.setAttribute("theme", "light");
        this.$vuetify.theme.dark = false;
      }
    },
    $route(){
      this.handleRedirect();
    }
  },
  methods: {
    logout(){
      var theme = localStorage.getItem('theme');
      localStorage.clear();
      if(theme != null){
        localStorage.setItem('theme', theme);
      }
      this.userData = null;
      delete axios.defaults.headers.common["Authorization"];
      this.$router.push("/login/");
    },
    navigateTo(url){
      if(this.$route.path != url)
        this.$router.push(url);
    },
    handleRedirect(){
      var path = this.$route.path;

      if(!ALLOW_UNAUTHORIZED.includes(path) && this.userData == null){
        this.$router.push("/login/");
      }

      if(DISPLAY_BLANK_URLS.includes(path)){
        this.appDisplay = "BLANK";
      }
      else{
        this.appDisplay = "DEFAULT";
        this.markNavigationPage();
        this.mainNavigation.model = false;
      }
    },
    markNavigationPage(){
      var path = this.$route.path;
      switch(path){
        case "/passwords/":
          this.mainNavigation.selected = 0;
          break;
        case "/boards/":
          this.mainNavigation.selected = 1;
          break;
        case "/profile/":
          this.mainNavigation.selected = 2;
          break;
        default:
          this.mainNavigation.selected = null;
      }
    },
    handleResize(){
      if(window.innerWidth < 960){
        if(this.appMode == "DESKTOP"){
          this.mainNavigation.model = false;
        }
        this.appMode = "MOBILE";
        this.mainNavigation.mobileAppBarModel = true;
      }
      else{
        this.appMode = "DESKTOP";
        this.mainNavigation.mobileAppBarModel = false;
      }
    },
    handleAuthorizationData(authorizationData){
      console.log(authorizationData);
      axios.defaults.headers.common['Authorization'] = "Bearer " + authorizationData.accessToken;
      localStorage.setItem('jwt_access', authorizationData.accessToken);
      localStorage.setItem('jwt_refresh', authorizationData.refreshToken);
      localStorage.setItem('user', JSON.stringify(authorizationData.userData));

      this.loadUserData(authorizationData.userData);
    },
    loadAcessToken(){
      var token = localStorage.getItem("jwt_access");
      console.log

      if(token != null){
        // TODO: validate expiration datetime

        axios.defaults.headers.common["Authorization"] = "Bearer " + token;
      }      
    },
    loadUserData(data = null){
      if(data != null){
        this.userData = data;
      }
      else{
        var stored = localStorage.getItem('user');
        if(stored != null){
          this.userData = JSON.parse(stored);
          console.log(stored);
        }
      }

      if(this.userData != null){
        var initials = "";
        if(this.userData.firstName != ""){
          initials += this.userData.firstName[0];
        }
        if(this.userData.lastName != ""){
          initials += this.userData.lastName[0];
        }
        initials = initials.toUpperCase();
        this.userData.initials = initials;
      }
      else{
        this.userData = null;
      }
    },
    loadTheme(){
      var value = localStorage.getItem('theme');
      if(value != null && value == "dark"){
        this.darkMode = true;
      }
      else{
        this.darkMode = false;
      }
    }
  }
};
</script>

<style scoped>
  .navbar-avatar {
    color: var(--v-primary-base);
  }

  .navigation-boards-list-group-item{
  }
</style>