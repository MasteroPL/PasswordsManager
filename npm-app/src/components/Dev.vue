<template>
  <v-container>
    <new-password-dialog
      ref="newPasswordDialog"
    ></new-password-dialog>
  </v-container>
</template>

<script>
  export default {
    name: 'Dev',

    data: () => ({
      userItems: [
        {
          id: 1,
          name: "User 1"
        },
        {
          id: 2,
          name: "User 2"
        },
        {
          id: 3,
          name: "User 3"
        },
        {
          id: 4,
          name: "User 4"
        },
      ]
    }),
    mounted() {
      var that = this;
      setTimeout(function(){
        that.$refs.newPasswordDialog.open();
      }, 1000);
    }
  }
</script>
