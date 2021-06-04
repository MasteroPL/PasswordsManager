<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="550"
  >
    <v-card>
      <v-toolbar>
        <v-toolbar-title>Utwórz hasło</v-toolbar-title>
      </v-toolbar>

      <v-card-text style="padding-top:10px">
        <v-text-field
            v-model="password"
            label="Hasło"
            :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            required
            :disabled="disabled"
            :type="showPassword ? 'text' : 'password'"
            @click:append="showPassword = !showPassword"
            :error-messages="passwordErrors"
            :maxlength="100"
            clearable
        ></v-text-field>

        <v-text-field
          v-model="title"
          label="Tytuł"
          required
          :disabled="disabled"
          :error-messages="titleErrors"
          :maxlength="50"
        ></v-text-field>

        <v-textarea
          v-model="description"
          label="Opis"
          :disabled="disabled"
          :error-messages="descriptionErrors"
          :maxlength="500"
          style="font-size:14px"
        ></v-textarea>
      </v-card-text>

      <div style="padding: 10px;" class="global-error" v-if="globalError != null && globalError != ''">
        {{ globalError }}
      </div>

      <v-progress-linear
        v-if="loading"
        indeterminate
        color="primary"
      ></v-progress-linear>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn
          text
          @click="cancel()"
          :disabled="disabled"
        >Anuluj</v-btn>
        <v-btn
          text
          color="primary"
          :disabled="disabled"
          @click="confirm"
        >Zatwierdź</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import appConfig from "../../../config"
  import axios from "axios"
  const DEFAULT_SUBMIT_URL = "api/password/new/";

  export default {
    name: 'NewPasswordDialog',

    data: () => ({
      dialog: false,
      loading: false,
      disabled: false,
      password: null,
      showPassword: false,
      passwordErrors: [],
      title: null,
      titleErrors: [],
      description: null,
      descriptionErrors: [],

      globalError: null
    }),
    mounted() {
      
    },
    props: {
      defaultPassword: {
        type: String,
        required: false,
        default: null
      },
      defaultTitle: {
        type: String,
        required: false,
        default: null
      },
      defaultDescription: {
        type: String,
        required: false,
        default: null
      }
    },
    methods: {
      open(){
        this.title = this.defaultTitle;
        this.password = this.defaultPassword;
        this.description = this.defaultDescription;

        this.dialog = true;
      },
      close(){
        this.dialog = false;
      },
      cancel(){
        this.dialog = false;
        this.$emit("cancelled");
      },
      confirm(){
        this.globalError = null;
        this.passwordErrors = [];
        this.titleErrors = [];
        this.descriptionErrors = [];
        var valid = true;
        if (this.password == null || this.password == ""){
          this.passwordErrors = [ "To pole jest wymagane" ];
          valid = false;
        }
        if(this.title == null || this.title == ""){
          this.titleErrors = [ "To pole jest wymagane" ];
          valid = false;
        }
        if(!valid){
          return;
        }

        // Emitting data
        var data = {
          password: this.password,
          title: this.title,
          description: (this.description == null || this.description == "") ? "Brak opisu" : this.description
        };
        this.$emit("confirmed", data);
      },
      startLoading(){
        this.loading = true;
      },
      stopLoading(){
        this.loading = false;
      },
      enable(){
        this.disabled = false;
      },
      disable(){
        this.disabled = true;
      },
      defaultSubmit(data){
        this.startLoading();
        this.disable();

        var that = this;
        return axios({
          url: appConfig.apiUrl + DEFAULT_SUBMIT_URL,
          method: "post",
          data: {
            password: data.password,
            title: data.title,
            description: data.description
          }
        }).then((req) => {
          that.stopLoading();
          that.enable();
          var response = req.data;

          return {
            status: "OK",
            data: response
          };
        }).catch((error) => {
          that.stopLoading();
          that.enable();

          if(error.response){
            if(error.response.status == 403 || error.response.status == 401){
              that.globalError = "Odmowa dostępu";
            }
            else if(error.response.status == 400){
              if(error.response.data["__all__"] !== undefined){
                that.globalError = "Wystąpił nierozpoznany błąd. Spróbuj ponownie później.";
              }
              else{
                if (error.response.data["password"] !== undefined){
                  if(error.response.data["password"][0][0] == "Max allowed password length is 100 characters"){
                    that.passwordErrors = [ "Maksymalna dozwolona długość hasła to 100 znaków" ];
                  }
                  else{
                    that.globalError = "Wystąpił nierozpoznany błąd dotyczący hasła. (" + error.response["password"][0][0] + ")";
                  }
                }
              }
            }

            return {
              status: "ERR",
              data: error.response
            };
          }
          else{
            that.globalError = "Błąd sieci. Spróbuj ponownie później.";
          }

          return {
            status: "ERR"
          };
        });
      }
    }
  }
</script>
