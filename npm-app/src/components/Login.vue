<template>
  <v-container class="fill-page" fill-height fluid>
    <v-row align="center" justify="center">
      <div style="text-align:center; max-width:210px;">
        <h1 class="app-title">PassManager</h1>
        <h3 style="margin-bottom: 20px;">Authorization</h3>

        <v-text-field
          v-model="login"
          label="Username"
          required
          :error-messages="loginErrors"
          maxlength=50
          @keyup.enter.native="handleSubmit"
        ></v-text-field>
        <v-text-field
          v-model="password"
          label="Password"
          :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          required
          :type="showPassword ? 'text' : 'password'"
          @click:append="showPassword = !showPassword"
          :error-messages="passwordErrors"
          maxlength=50
          @keyup.enter.native="handleSubmit"
        ></v-text-field>

        <div style="padding: 10px;" class="global-error" v-if="globalError != null && globalError != ''">
          {{ globalError }}
        </div>

        <v-btn
          style="margin-top: 20px;"
          color="primary"
          @click="handleSubmit()"

          v-if="mode == 'DEFAULT'"
        >Log in</v-btn>

        <v-progress-circular
          style="margin-top: 24px;"
          v-else
          indeterminate
          color="primary"
        ></v-progress-circular>
      </div>
    </v-row>
  </v-container>
</template>

<script>
  import appConfig from "../config"
  import axios from "axios"

  export default {
    name: 'Login',

    mounted(){
    },

    data: () => ({
      // Modes:
      // - DEFAULT
      // - SENDING
      mode: "DEFAULT",

      globalError: null,
      login: "",
      loginErrors: [],
      password: "",
      passwordErrors: [],
      showPassword: false
    }),

    methods: {
      async handleSubmit(){
        // Initial validation
        var valid = true;
        this.loginErrors = [];
        this.passwordErrors = [];
        this.globalError = null;
        if(this.login == "" || this.login == null){
          this.loginErrors = [ "This field is required" ];
          valid = false;
        }
        if(this.password == "" || this.password == null){
          this.passwordErrors = [ "This field is required" ];
          valid = false;
        }

        if(valid){
          delete axios.defaults.headers.common["Authorization"];
          // Request
          this.mode = "SENDING";
          var that = this;
          axios({
            method: "post",
            url: appConfig.apiUrl + 'api/token/',
            data: {
              login: this.login,
              password: this.password
            }
          }).then((req) => {
            // Successful login
            var response = req.data;
            var userData = {
              id: response.payload.id,
              firstName: response.payload.first_name,
              lastName: response.payload.last_name,
              email: response.payload.email,
              dateJoined: response.payload.date_joined,
              username: response.payload.username,
              isActive: response.payload.is_active
            };
            this.$store.commit({
              type: 'setTokens',
              accessToken: response.access,
              refreshToken: response.refresh
            });
            this.$store.commit("setUserPayload",
              userData
            );
            that.$emit('reload-data');
            that.$router.push("/boards/");
          }).catch((error) => {
            if(error.response){
              // Standard error in validation
              if(error.response.status == 400){
                if(error.response.data["__global__"] !== undefined){
                  var err = error.response.data["__global__"][0];
                  switch(err){
                    case "Invalid username or password":
                      this.globalError = "Invalid username or password";
                      break;

                    default:
                      this.globalError = "Data validation error occured";
                  }
                }
              }
              else if(error.response.status == 403 || error.response.status == 401){
                this.globalError = "Access forbidden";
              }
              else if(error.response.status == 429){
                this.globalError = "Request throttled. Wait a minute before attempting again.";
              }
              else {
                this.globalError = "An unrecognized error has occured";
              }
            }
            else{
              this.globalError = "Network error. Please try again later.";
            }
          }).finally(() => {
            that.mode = "DEFAULT";
          });
          
        }
      }
    }
  }
</script>

<style scoped>
.fill-page{
  position: fixed;
  height: 100%;
  width: 100%;
  top: 0;
  left: 0;
}
.app-title{
  color: var(--v-primary-base);
}
</style>