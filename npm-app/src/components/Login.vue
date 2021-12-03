<template>
  <v-container class="fill-page" fill-height fluid>
    <v-row align="center" justify="center">
      <div style="text-align:center; max-width:210px;">
        <h1 class="app-title">PassManager</h1>
        <h3 style="margin-bottom: 20px;">Logowanie</h3>

        <v-text-field
          v-model="login"
          label="Nazwa użytkownika"
          required
          :error-messages="loginErrors"
          maxlength=50
          @keyup.enter.native="handleSubmit"
        ></v-text-field>
        <v-text-field
          v-model="password"
          label="Hasło"
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
        >Zaloguj</v-btn>

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
          this.loginErrors = [ "To pole jest wymgane" ];
          valid = false;
        }
        if(this.password == "" || this.password == null){
          this.passwordErrors = [ "To pole jest wymagane" ];
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
            that.$emit('authorization-data-received', {
              userData: userData,
              accessToken: response.access,
              refreshToken: response.refresh
            });
            that.$router.push("/boards/");
          }).catch((error) => {
            if(error.response){
              // Standard error in validation
              if(error.response.status == 400){
                if(error.response.data["__global__"] !== undefined){
                  var err = error.response.data["__global__"][0];
                  switch(err){
                    case "Invalid username or password":
                      this.globalError = "Nieprawidłowy login lub hasło";
                      break;

                    default:
                      this.globalError = "Wystąpił nierozpoznany błąd walidacji danych";
                  }
                }
              }
              else if(error.response.status == 403 || error.response.status == 401){
                this.globalError = "Dostęp zabroniony";
              }
              else if(error.response.status == 429){
                this.globalError = "Zapytanie zablokowane. Odczekaj minutę przed następną próbą.";
              }
              else {
                this.globalError = "Wystąpił nierozpoznany błąd";
              }
            }
            else{
              this.globalError = "Błąd sieci. Spróbuj ponownie później.";
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