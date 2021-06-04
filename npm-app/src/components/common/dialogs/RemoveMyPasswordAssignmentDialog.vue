<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="320"
  >
    <v-card>
      <v-toolbar>
        <v-toolbar-title>Usuń hasło</v-toolbar-title>
      </v-toolbar>

      <v-card-text style="padding-top: 20px">
        Czy na pewno chcesz usunąć hasło?
        <br /><br />
        Hasło zostanie usunięte tylko z Twojego konta. Pozostali użytkownicy nadal będą mieli do niego dostęp.
      </v-card-text>

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
          color="red"
          :disabled="disabled"
          @click="confirm()"
        >Usuń</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import appConfig from "@/config"
  import axios from "axios"
  const DEFAULT_SUBMIT_URL = "api/password/{PASSWORD_CODE}/deassign-me/";

  export default {
    name: "RemoveMyPasswordAssignmentDialog",
    data: () => ({
      dialog: false,
      loading: false,
      disabled: false,
      globalError: null      
    }),
    mounted() {

    },
    props: {

    },
    methods: {
      open(){
        this.disabled = false;
        this.loading = false;
        this.globalError = null;
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
        this.$emit("confirmed");
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
      defaultSubmit(passwordCode){
        this.startLoading();
        this.disable();

        var that = this;
        var submitUrl = DEFAULT_SUBMIT_URL.replace("{PASSWORD_CODE}", passwordCode);
        return axios({
          url: appConfig.apiUrl + submitUrl,
          method: "delete"
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
            else{
              that.globalError = "Wystąpił nierozpoznany błąd";
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

<style scoped>

</style>