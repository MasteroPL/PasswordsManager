
<template>

  <v-dialog
    v-model="dialog"
    persistent
    max-width="550"
  >
    <v-card>
      <v-toolbar>
        <v-toolbar-title>Edytuj hasło</v-toolbar-title>
      </v-toolbar>

      <v-card-text style="padding-top:20px">
        <v-row align="center" style="padding: 0 12px; position: relative">
          <v-checkbox
            v-model="updatePasswordValueEnabled"
            hide-details
            :disabled="disabled"
            class="shrink mr-2 mt-0"
          ></v-checkbox>
          <v-text-field
            ref="newPasswordValueField"
            v-model="newPasswordValue"
            :disabled="!updatePasswordValueEnabled || disabled"
            label="Nowa wartość hasła"
            :append-icon="showPasswordValue ? 'mdi-eye' : 'mdi-eye-off'"
            :type="showPasswordValue ? 'text' : 'password'"
            :error-messages="newPasswordValueErrors"
            :maxlength="100"
            @click:append="showPasswordValue = !showPasswordValue"
            clearable
          ></v-text-field>
          
          <div 
            v-if="!updatePasswordValueEnabled" 
            class="password-field-overlayer"
            @click="focusPasswordValueField()"
          ></div>
        </v-row>

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
  import appConfig from "@/config"
  import axios from "axios"
  const DEFAULT_SUBMIT_URL = "api/password/{PASSWORD_CODE}/edit/";

  export default {
    name: "EditPasswordDialog",
    data: () => ({
      dialog: false,
      loading: false,
      disabled: false,
      globalError: null,

      updatePasswordValueEnabled: false,
      newPasswordValue: "",
      showPasswordValue: false,
      newPasswordValueErrors: [],
      
      title: null,
      titleChanged: false,
      titleErrors: [],
      description: null,
      descriptionChanged: false,
      descriptionErrors: []
    }),
    mounted() {

    },
    props: {
      defaultNewPasswordValue: {
        type: String,
        required: false,
        default: null
      },
      defaultUpdatePasswordValueEnabled: {
        type: Boolean,
        required: false,
        default: false
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
    watch: {
      "title": function(){
        this.titleChanged = true;
      },
      "description": function(){
        this.descriptionChanged = true;
      }
    },
    methods: {
      open(){
        this.updatePasswordValueEnabled = this.defaultUpdatePasswordValueEnabled;
        this.newPasswordValue = this.defaultNewPasswordValue;
        this.title = this.defaultTitle;
        this.description = this.defaultDescription;

        this.titleChanged = false;
        this.descriptionChanged = false;

        this.dialog = true;
      },
      close(){
        this.dialog = false;
      },
      cancel(){
        this.close();
        this.$emit("cancelled");
      },
      confirm(){
        this.globalError = null;
        this.newPasswordValueErrors = [];
        this.titleErrors = [];
        this.descriptionErrors = [];
        var valid = true;

        if(this.updatePasswordValueEnabled && (this.newPasswordValue == null || this.newPasswordValue == "")){
          this.newPasswordValueErrors = [ "To pole nie może być puste" ];
          valid = false;
        }
        if(this.title == null || this.title == ""){
          this.titleErrors = [ "To pole jest wymagane" ];
          valid = false;
        }
        if(!valid){
          return;
        }

        var tmpDesc = (this.description == null || this.description == "") ? "Brak opisu" : this.description;

        var result = {
          newPassword: (this.updatePasswordValueEnabled) ? this.newPasswordValue : null,
          title: (this.titleChanged) ? this.title : null,
          description: (this.descriptionChanged) ? tmpDesc : null
        };

        this.$emit("confirmed", result);
      },
      focusPasswordValueField(){
        if(this.disabled) return;

        var that = this;
        this.updatePasswordValueEnabled = true;
        setTimeout(function() {
          that.$refs.newPasswordValueField.$refs.input.focus();
        }, 1);
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
      defaultSubmit(data, passwordCode){
        this.startLoading();
        this.disable();

        var that = this;
        var submitUrl = DEFAULT_SUBMIT_URL.replace("{PASSWORD_CODE}", passwordCode);
        return axios({
          url: appConfig.apiUrl + submitUrl,
          method: "patch",
          data: {
            new_password: data.newPassword,
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
              // NewPassword errors
              if (error.response.data["new_password"] !== undefined){
                // Password longer than 100 charcters
                if(error.response.data["new_password"][0]["code"] == "PASSWORD_TOO_LONG"){
                  that.newPasswordValueErrors = [ "Hasło nie może przekraczać 100 znaków" ];
                }
                else {
                  that.newPasswordValueErrors = [ "Wystąpił nierozpoznany błąd" ];
                }
              } 
              // Title errors
              if (error.response.data["title"] !== undefined){
                // Title longer than 50 characters
                if(error.response.data["title"][0]["code"] == "TITLE_TOO_LONG"){
                  that.titleErrors = [ "Tytuł nie może przekraczać 50 znaków" ];
                }
                else{
                  that.titleErrors = [ "Wystąpił nierozpoznany błąd" ];
                }
              }
              // Description errors
              if(error.response.data["description"] !== undefined){
                // Description longer than 500 characters
                if(error.response.data["description"][0]["code"] == "DESCRIPTION_TOO_LONG"){
                  that.descriptionErrors = [ "Opis nie może przekraczać 500 znaków" ];
                }
                else{
                  that.descriptionErrors = [ "Wystąpił nierozpoznany błąd" ];
                }
              }
            }
            else {
              that.globalError = "Wystąpił nierozpoznany błąd";
            }

            return {
              status: "ERR",
              data: error.response
            };
          }
          else {
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

<style scoped>
  .password-field-overlayer {
    position: absolute;
    top: 0;
    left: 48px;
    width: calc(100% - 48px);
    height: 100%;
  }
</style>