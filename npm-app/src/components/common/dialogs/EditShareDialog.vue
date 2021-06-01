
<template>
  <div>
    <v-dialog
      v-model="dialog"
      persistent
      max-width="320"
    >
      <v-card>
        <v-toolbar>
          <v-toolbar-title>Edytuj udostępnienie</v-toolbar-title>
          <!--<template v-slot:extension v-if="passwordTitleSlot != null || usernameSlot != null">
            <div class="share-subtitle">
              <span v-if="passwordTitleSlot != null">{{ passwordTitleSlot }}</span>
              <span v-if="passwordTitleSlot != null && usernameSlot != null"><br /></span>
              <span v-if="usernameSlot != null">{{ usernameSlot }}</span>
            </div>
          </template>-->
        </v-toolbar>

        <v-card-text style="padding-top:10px">
          <v-text-field
              label="Użytkownik"
              v-if="usernameSlot != null"
              :disabled="true"
              v-model="usernameSlot"
          ></v-text-field>

          <!-- Permissions section -->

          <!-- READ -->
          <v-checkbox
            class="dense-checkbox"
            v-model="permissionRead"
            :disabled="permissionOwner || disabled"
            v-if="allowPermissionRead"
          >
            <template v-slot:label>
              <div>
                Odczyt
                <v-tooltip bottom>
                  <template v-slot:activator="{on}">
                    <v-icon
                      color="secondary"
                      v-on="on"
                      small
                    >mdi-help-circle-outline</v-icon>
                  </template>

                  <span>Użytkownik będzie mógł odczytać to hasło</span>
                </v-tooltip>
              </div>
            </template>
          </v-checkbox>

          <!-- SHARE -->
          <v-checkbox
            class="dense-checkbox"
            v-model="permissionShare"
            :disabled="permissionOwner || disabled"
            v-if="allowPermissionShare"
          >
            <template v-slot:label>
              <div>
                Udostępnianie
                <v-tooltip bottom>
                  <template v-slot:activator="{on}">
                    <v-icon
                      color="secondary"
                      v-on="on"
                      small
                    >mdi-help-circle-outline</v-icon>
                  </template>

                  <span>Użytkownik będzie mógł udostępnić to hasło innym użytkownikom do odczytu. (Tylko do odczytu!)</span>
                </v-tooltip>
              </div>
            </template>
          </v-checkbox>

          <!-- UPDATE -->
          <v-checkbox
            class="dense-checkbox"
            v-model="permissionUpdate"
            :disabled="permissionOwner || disabled"
            v-if="allowPermissionUpdate"
          >
            <template v-slot:label>
              <div>
                Aktualizowanie
                <v-tooltip bottom>
                  <template v-slot:activator="{on}">
                    <v-icon
                      color="secondary"
                      v-on="on"
                      small
                    >mdi-help-circle-outline</v-icon>
                  </template>

                  <span>Użytkownik będzie mógł aktualizować (zmieniać) to hasło</span>
                </v-tooltip>
              </div>
            </template>
          </v-checkbox>

          <!-- OWNER -->
          <v-checkbox
            class="dense-checkbox"
            v-model="permissionOwner"
            :disabled="disabled"
            v-if="allowPermissionOwner"
          >
            <template v-slot:label>
              <div>
                Administrowanie
                <v-tooltip bottom>
                  <template v-slot:activator="{on}">
                    <v-icon
                      color="secondary"
                      v-on="on"
                      small
                    >mdi-help-circle-outline</v-icon>
                  </template>

                  <span>Użytkownik będzie mógł administrować tym hasłem. Oznacza to dostęp do odczytu, udostępniania, aktualizowania, usuwania udostępnień</span>
                </v-tooltip>
              </div>
            </template>
          </v-checkbox>
        </v-card-text>

        <div style="padding: 10px;" class="global-error" v-if="!deletePrompt.dialog && globalError != null && globalError != ''">
          {{ globalError }}
        </div>

        <v-progress-linear
          v-if="loading && !deletePrompt.dialog"
          indeterminate
          color="primary"
        ></v-progress-linear>

        <v-card-actions>
          <v-btn
            text
            color="red"
            :disabled="disabled"
            @click="deletePromptOpen()"
          >Usuń</v-btn>

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

    <!-- Delete confirmation prompt -->
    <v-dialog
      v-model="deletePrompt.dialog"
      max-width="280"
      persistent
    >
      <v-card>
        <v-toolbar>
          <v-toolbar-title>
            Usuń udostępnienie
          </v-toolbar-title>
        </v-toolbar>

        <v-card-text style="padding-top: 20px;">
          Czy na pewno chcesz usunąć udostępnienie?
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
            @click="deletePrompt.dialog = false"
            :disabled="disabled"
          >Nie</v-btn>
          <v-btn
            text
            color="red"
            :disabled="disabled"
            @click="deletePromptConfirm()"
          >Usuń</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
  
  export default {
    name: 'EditShareDialog',

    data: () => ({
      dialog: false,
      loading: false,
      disabled: false,

      permissionRead: false,
      permissionShare: false,
      permissionUpdate: false,
      permissionOwner: false,

      globalError: null,


      deletePrompt: {
        dialog: false
      }
    }),
    mounted() {

    },
    props: {
      // Slots
      usernameSlot: {
        type: String,
        required: false,
        default: null
      },

      // Which permission checkboxes should be available to pick?
      allowPermissionRead: {
        type: Boolean,
        required: false,
        default: true
      },
      allowPermissionShare: {
        type: Boolean,
        required: false,
        default: true
      },
      allowPermissionUpdate: {
        type: Boolean,
        required: false,
        default: true
      },
      allowPermissionOwner: {
        type: Boolean,
        required: false,
        default: true
      },

      // What should be the initial values of the permission checkboxes upon opening the dialog?
      defaultPermissionRead: {
        type: Boolean,
        required: false,
        default: false
      },
      defaultPermissionShare: {
        type: Boolean,
        required: false,
        default: false
      },
      defaultPermissionUpdate: {
        type: Boolean,
        required: false,
        defualt: false
      },
      defaultPermissionOwner: {
        type: Boolean,
        required: false,
        default: false
      }
    },
    methods: {
      open(){
        this.permissionRead = this.defaultPermissionRead && this.allowPermissionRead;
        this.permissionShare = this.defaultPermissionShare && this.allowPermissionShare;
        this.permissionUpdate = this.defaultPermissionUpdate && this.allowPermissionUpdate;
        this.permissionOwner = this.defaultPermissionOwner && this.allowPermissionOwner;

        this.deletePrompt.dialog = false;
        this.globalError = null;
        this.loading = false;
        this.disabled = false;

        this.dialog = true;
      },
      close() {
        this.dialog = false;
        this.deletePrompt.dialog = false;
      },
      cancel(){
        this.close();
        this.$emit("cancelled");
      },
      confirm(){
        var result = {
          read: this.permissionRead && this.allowPermissionRead,
          share: this.permissionShare && this.allowPermissionShare,
          update: this.permissionUpdate && this.allowPermissionUpdate,
          owner: this.permissionOwner && this.allowPermissionOwner
        };

        if(result.owner){
          result.read = true;
          result.share = true;
          result.update = true;
        }

        this.$emit("confirmed", result);
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
      deletePromptOpen(){
        this.deletePrompt.dialog = true;
      },
      deletePromptConfirm(){
        this.$emit("delete");
      },

      defaultSubmit(assignmentId, data){
        console.log(assignmentId);
        console.log(data);
      }
    }
  }
</script>

<style scoped>
  .share-subtitle{
    font-size: 12px;
  }
  .share-subtitle {
    color: rgba(0, 0, 0, 0.6);
  }
  .theme--dark .share-subtitle {
    color: rgba(255, 255, 255, 0.7);
  }
</style>