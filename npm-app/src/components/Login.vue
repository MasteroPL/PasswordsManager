<template>
  <v-container class="fill-page" fill-height fluid>
    <v-row align="center" justify="center">
      <div style="text-align:center; max-width:320px;">
        <h1 class="app-title">PassManager</h1>
        <h3 style="margin-bottom: 20px;">Logowanie</h3>

        <v-text-field
          v-model="login"
          label="Nazwa użytkownika"
          required
        ></v-text-field>
        <v-text-field
          v-model="password"
          label="Hasło"
          :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          required
          :type="showPassword ? 'text' : 'password'"
          @click:append="showPassword = !showPassword"
        ></v-text-field>

        <v-btn
          style="margin-top: 20px;"
          color="primary"
        >Zaloguj</v-btn>
      </div>
    </v-row>
  </v-container>
</template>

<script>
  export default {
    name: 'Login',

    data: () => ({
      login: "",
      password: "",
      showPassword: false
    }),
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