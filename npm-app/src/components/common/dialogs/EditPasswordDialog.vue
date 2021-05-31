
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
      titleErrors: [],
      description: null,
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
    methods: {
      open(){
        this.updatePasswordValueEnabled = this.defaultUpdatePasswordValueEnabled;
        this.newPasswordValue = this.defaultNewPasswordValue;
        this.title = this.defaultTitle;
        this.description = this.defaultDescription;

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

        var result = {
          updatePasswordEnabled: this.updatePasswordValueEnabled,
          newPassword: (this.updatePasswordValueEnabled) ? this.newPasswordValue : null,
          title: this.title,
          description: (this.description == null || this.description == "") ? "Brak opisu" : this.description
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