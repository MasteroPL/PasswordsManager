<template>
  <div>
    <v-dialog
      v-model="dialog"
      persistent
      max-width="320"
    >
      <v-card>
        <v-toolbar

        >
          <v-toolbar-title>Zmień właściciela hasła</v-toolbar-title>
        </v-toolbar>

        <v-card-text style="padding-top:20px">
          <v-autocomplete
            v-model="userId"
            :items="items"
            :loading="userLoading"
            item-text="name"
            item-value="id"
            :search-input.sync="userSearch"
            label="Wybierz użytkownika"
            hide-no-data
            placeholder="Zacznij pisać aby wyszukać"
            :disabled="disabled"
            clearable
            
            :error-messages="userErrors"
          ></v-autocomplete>
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
            @click="confirm()"
          >Zatwierdź</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Confirmation prompt -->
    <v-dialog
      v-model="confirmationPrompt.dialog"
      max-width="280"
      persistent
    >
      <v-card>
        <v-toolbar>
          <v-toolbar-title>
            Potwierdź zmianę właściciela
          </v-toolbar-title>
        </v-toolbar>

        <v-card-text style="padding-top: 20px;">
          Czy na pewno chcesz przepisać właścicielstwo hasła na użytkownika <b>{{ getUsernameFromId(userId) }}</b>?

          Uprawnienia twórcy hasła zostaną przeniesione na wybranego użytkownika. Nadal będziesz miał uprawnienia administratora.
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
            @click="confirmationPrompt.dialog = false"
            :disabled="disabled"
          >Nie</v-btn>
          <v-btn
            text
            color="red"
            :disabled="disabled"
            @click="confirmationPromptConfirm()"
          >Usuń</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
  import axios from "axios"

  export default {
    name: "ChangePasswordOwnerDialog",
    data: () => ({
      dialog: false,
      loading: false,
      disabled: false,
      globalError: null,

      userId: null,
      userSearch: "",
      userLoading: false,
      currentUpdateId: 0,
      preventUpdate: false,
      searchTimeout: null,
      userErrors: [],
      items: [
        // {
        //   id: 1,
        //   name: "User 1"
        // }
      ],

      confirmationPrompt: {
        dialog: false
      }
    }),
    watch: {
      "userSearch": function(){
        if(this.userSelectionAPI == null) return;

        if(!this.preventUpdate){
          if(this.searchTimeout != null){
            clearTimeout(this.searchTimeout);
          }
          var that = this;
          this.searchTimeout = setTimeout(function(){
            that.invokeUpdateUserAutocomplete();
          }, 500);
        }
        else{
          this.preventUpdate = false;
        }
      },
      "userId": function(){
        this.preventUpdate = true;
      }
    },
    mounted() {

    },
    props: {
      userSelectionUseAPI: {
        type: Boolean,
        required: false,
        default: false
      },
      userSelectionAPI: {
        type: Object,
        required: false,
        default: null
      },
      userSelectionAPILoadInitial: {
        type: Boolean,
        required: false,
        default: true
      },
      userSelectionItems: {
        type: Array,
        required: false,
        default: null
      },
    },
    methods: {
      APIUpdateUserAutocomplete(search){
        var updateId = ++this.currentUpdateId;
        this.userLoading = true;

        var that = this;
        axios({
          method: "GET",
          url: that.userSelectionAPI.url + `?search=${search}`,
          headers: that.userSelectionAPI.headers
        }).then((req) => {
          if(updateId == that.currentUpdateId){
            that.userLoading = false;
            var response = req.data;
            that.items = [];
            var tmp;
            for(var i = 0; i < response.length; i++){
              tmp = response[i];
              that.items.push({
                id: tmp.id,
                name: tmp.username + " (" + tmp.email + ")"
              });
            }
          }
        });
      },
      getUsernameFromId(userId){
        for(var i = 0; i < this.items.length; i++){
          if(this.items[i].id == userId){
            return this.items[i].name;
          }
        }
        return null;
      },
      open(){
        this.resetDialog();

        this.dialog = true;
      },
      close() {
        this.dialog = false;
        this.confirmationPrompt.dialog = false;
      },
      cancel(){
        this.close();
        this.$emit("cancelled");
      },
      confirm(){
        this.userErrors = [];
        this.globalError = null;
        if(this.userId == null){
          this.userErrors = [ "To pole jest wymagane" ];
          return;
        }

        this.confirmationPromptOpen();
      },
      disable(){
        this.disabled = true;
      },
      enable(){
        this.disabled = false;
      },
      startLoading(){
        this.loading = true;
      },
      stopLoading(){
        this.loading = false;
      },
      /**
       * Prompt asking for confirmation of delete action
       */
      confirmationPromptOpen(){
        this.confirmationPrompt.dialog = true;
      },
      confirmationPromptConfirm(){
        var result = {
          userId: this.userId,
          username: this.getUsernameFromId(this.userId)
        };

        this.$emit("confirmed", result);
      },

      defaultSubmit(passwordId, userId){
        console.log(passwordId);
        console.log(userId);
      },

      invokeUpdateUserAutocomplete() {
        if(this.userSearch != null && this.userSearch != ""){
          this.APIUpdateUserAutocomplete(this.userSearch);
        }
      },

      resetUserAutocomplete(){
        if(this.userSelectionUseAPI){
          if(this.userSelectionAPILoadInitial){
            this.APIUpdateUserAutocomplete("");
          }
          else if(this.userSelectionItems != null){
            this.items = this.userSelectionItems;
          }
          else{
            this.items = [];
          }
        }
        else{
          if(this.userSelectionItems != null){
            this.items = this.userSelectionItems;
          }
          else{
            this.items = [];
          }
        }
      },

      resetDialog(){
        this.resetUserAutocomplete();
        this.loading = false;
        this.disabled = false;
        this.globalError = null;
        this.userErrors = [];
        this.confirmationPrompt.dialog = false;
      }
    }
  }
</script>

<style scoped>

</style>