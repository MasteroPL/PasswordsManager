<template>
  <v-container>
    <share-dialog
      ref="shareDialog"
      :userSelectionItems="userItems"
    ></share-dialog>
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
      this.$refs.shareDialog.open();

      var that = this;
      setTimeout(function(){
        that.$refs.shareDialog.disable();
        that.$refs.shareDialog.startLoading();
      }, 1000);
      setTimeout(function(){
        that.$refs.shareDialog.enable();
        that.$refs.shareDialog.stopLoading();
        that.$refs.shareDialog.shareForUser.user.errors = ["Użytkownik nie istnieje"];
      }, 2000);
      setTimeout(function(){
        that.$refs.shareDialog.shareForUser.user.errors = [];
      }, 3000);
    }
  }
</script>
