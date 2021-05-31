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

      <v-card-text style="padding-top:10px;">
        Czy na pewno chcesz usunąć hasło?
        <br /><br />
        Usunięcie hasła spowoduje kompletne wymazanie go z pamięci. Nie będzie możliwe późniejsze odzyskanie hasła. Wszyscy przypisani użytkownicy stracą do niego dostęp.
        <br /><br />
        Jeśli chcesz usunąć hasło tylko dla siebie, przepisz najpierw właścicielstwo hasła na innego użytkownika i spróbuj ponownie.
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
          color="red"
          :disabled="disabled"
          @click="confirm()"
        >Usuń</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  export default {
    name: "DeletePasswordDialog",
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
      }
    }
  }
</script>

<style scoped>

</style>