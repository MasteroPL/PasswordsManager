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
      }
    }
  }
</script>

<style scoped>

</style>