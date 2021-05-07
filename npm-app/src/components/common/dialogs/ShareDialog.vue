<!--
How to use

Most important methods:
- open(resetDialog = true)
- close()
- disable()
- enable()
- startLoading()
- stopLoading()

Emits:
- cancelled
- confirmed, {
  shareFor: "USER"|"BOARD",
  userId|boardingId: {Number},
  permissionRead: {Boolean},
  permissionShare: {Boolean},
  permissionUpdate: {Boolean},
  permissionOwner: {Boolean}
}

Available props:
- defaultTabDisplayed: 0 (share for a user) / 1 (share for a board)

- userSelectionUseAPI: true/false; should the dialog use an API to retrieve possible choices?
- userSelectionAPI: Object {
  url: {string},
  headers: {Object}, // additional headers, like authorization, that should be appended
  data: {Object} // additional data for the request (the dialog only sends the search string on its own),
  [searchStringName]: {string} // optional, by default the search string is send as "search_string", you can redefine this behaviour
}
- userSelectionAPILoadInitial: true/false; should the dialog load initial data by sending an empty search string to the API?
- userSelectionItems: Array [
  { id: {Number}, name: {String} },
  ...
]; this array is used as choices list if userSelectionUseAPI is false or as initial data set if userSelectionAPILoadInitial is false

- boardSelectionUseAPI: true/false; should the dialog use an API to retrieve possible choices?
- boardSelectionAPI: Object {
  url: {string},
  headers: {Object}, // additional headers, like authorization, that should be appended
  data: {Object} // additional data for the request (the dialog only sends the search string on its own),
  [searchStringName]: {string} // optional, by default the search string is send as "search_string", you can redefine this behaviour
}
- boardSelectionAPILoadInitial: true/false; should the dialog load initial data by sending an empty search string to the API?
- boardSelectionItems: Array [
  { id: {Number}, name: {String} },
  ...
]; this array is used as choices list if userSelectionUseAPI is false or as initial data set if userSelectionAPILoadInitial is false

- allowPermissionRead: true/false; defines whether the checkbox for permission "READ" will be visible
- allowPermissionShare: true/false
- allowPermissionUpdate: true/false
- allowPermissionOwner: true/false

- defaultUserPermissionRead: true/false; defines whether the checkbox will be checked by default
- defaultUserPermissionShare: true/false
- defaultUserPermissionUpdate: true/false
- defaultUserPermissionOwner: true/false
- defaultBoardPermissionRead: true/false
- defaultBoardPermissionShare: true/false
- defaultBoardPermissionUpdate: true/false
- defaultBoardPermissionOwner: true/false

-->

<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="320"
  >
    <v-card>
      <!-- Small navigation panel. You can either share a password to a single user or a whole board -->
      <v-toolbar
      >
        <v-toolbar-title>Udostępnij hasło</v-toolbar-title>

        <template v-slot:extension>
          <v-tabs
            v-model="tab"
            fixed-tabs
          >
            <v-tabs-slider></v-tabs-slider>

            <v-tab :disabled="disabled">Użytkownik</v-tab>

            <v-tab :disabled="disabled">Tablica</v-tab>
          </v-tabs>
        </template>
      </v-toolbar>

      <v-tabs-items v-model="tab">
        <!-- Sharing for user -->
        <v-tab-item>
          <v-card>
            <v-card-text>
              <v-autocomplete
                v-model="shareForUser.user.model"
                :items="shareForUser.user.items"
                :loading="shareForUser.user.loading"
                :search-input.sync="shareForUser.user.search"
                item-text="name"
                item-value="id"
                label="Wybierz użytkownika"
                hide-no-data
                placeholder="Zacznij pisać aby wyszukać"
                :disabled="disabled"
                clearable

                :error-messages="shareForUser.user.errors"
              ></v-autocomplete>

              <!-- Access permissions -->
              <v-checkbox
                  class="dense-checkbox"
                  v-model="shareForUser.permissionRead"
                  :disabled="shareForUser.permissionOwner || disabled"
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

                      <span>Użytkownik będziem mógł odczytać to hasło</span>
                    </v-tooltip>
                  </div>
                </template>
              </v-checkbox>
              <v-checkbox
                  class="dense-checkbox"
                  v-model="shareForUser.permissionShare"
                  :disabled="shareForUser.permissionOwner || disabled"
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
              <v-checkbox
                  class="dense-checkbox"
                  v-model="shareForUser.permissionUpdate"
                  :disabled="shareForUser.permissionOwner || disabled"
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
              <v-checkbox
                  class="dense-checkbox"
                  v-model="shareForUser.permissionOwner"
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
          </v-card>
        </v-tab-item>

        <!-- Sharing for board -->
        <v-tab-item>
          <v-card>
            <v-card-text>
              <v-autocomplete
                v-model="shareForBoard.board.model"
                :items="shareForBoard.board.items"
                :loading="shareForBoard.board.loading"
                :search-input.sync="shareForBoard.board.search"
                item-text="name"
                item-value="id"
                label="Wybierz tablicę"
                hide-no-data
                placeholder="Zacznij pisać aby wyszukać"
                :disabled="disabled"
                clearable

                :error-messages="shareForBoard.board.errors"
              ></v-autocomplete>

              <!-- Access permissions -->
              <v-checkbox
                  class="dense-checkbox"
                  v-model="shareForBoard.permissionRead"
                  :disabled="shareForBoard.permissionOwner || disabled"
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

                      <span>Użytkownicy z dostępem do odczytu haseł dla danej tablicy będą mogli odczytać to hasło</span>
                    </v-tooltip>
                  </div>
                </template>
              </v-checkbox>
              <v-checkbox
                  class="dense-checkbox"
                  v-model="shareForBoard.permissionShare"
                  :disabled="shareForBoard.permissionOwner || disabled"
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

                      <span>Użytkownicy z dostępem do udostępniania haseł dla danej tablicy będą mogli udostępnić to hasło innym użytkownikom do odczytu. (Tylko do odczytu!)</span>
                    </v-tooltip>
                  </div>
                </template>
              </v-checkbox>
              <v-checkbox
                  class="dense-checkbox"
                  v-model="shareForBoard.permissionUpdate"
                  :disabled="shareForBoard.permissionOwner || disabled"
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

                      <span>Użytkownicy z dostępem do aktualizowania haseł dla danej tablicy będą mogli zaktualizować (zmienić) to hasło</span>
                    </v-tooltip>
                  </div>
                </template>
              </v-checkbox>
              <v-checkbox
                  class="dense-checkbox"
                  v-model="shareForBoard.permissionOwner"
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

                      <span>Użytkownicy z dostępem do administrowania hasłami dla danej tablicy będą mogli administrować tym hasłem. Oznacza to dostęp do odczytu, udostępniania, aktualizowania, usuwania udostępnień</span>
                    </v-tooltip>
                  </div>
                </template>
              </v-checkbox>
            </v-card-text>
          </v-card>
        </v-tab-item>
      </v-tabs-items>

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
        >Udostępnij</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import axios from 'axios'

  export default {
    name: 'ShareDialog',

    props: {
      defaultTabDisplayed: {
        type: Number,
        required: false,
        default: 0
      },

      //
      // Default permissions
      //
      defaultUserPermissionRead: {
        type: Boolean,
        required: false,
        default: true
      },
      defaultUserPermissionShare: {
        type: Boolean,
        required: false,
        default: false
      },
      defaultUserPermissionUpdate: {
        type: Boolean,
        required: false,
        default: false
      },
      defaultUserPermissionOwner: {
        type: Boolean,
        required: false,
        default: false
      },
      defaultBoardPermissionRead: {
        type: Boolean,
        required: false,
        default: true
      },
      defaultBoardPermissionShare: {
        type: Boolean,
        required: false,
        default: true
      },
      defaultBoardPermissionUpdate: {
        type: Boolean,
        required: false,
        default: true
      },
      defaultBoardPermissionOwner: {
        type: Boolean,
        required: false,
        default: true
      },

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

      //
      // User selection
      //
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
      // Initial meaning we just take a shot to the API with empty search string
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

      // Board selection
      boardSelectionUseAPI: {
        type: Boolean,
        required: false,
        default: false
      },
      boardSelectionAPI: {
        type: Object,
        required: false,
        default: null
      },
      // Initial meaning we just take a shot to the API with empty search string
      boardSelectionAPILoadInitial: {
        type: Boolean,
        required: false,
        default: true
      },
      boardSelectionItems: {
        type: Array,
        required: false,
        default: null
      }
    },

    data: () => ({
      dialog: false,
      tab: 0,
      disabled: false,
      loading: false,
      globalError: null,
      shareForUser: {
        user: {
          model: null,
          search: "",
          searchTimeout: null,
          currentUpdateId: 0,
          preventUpdate: false,
          loading: false,
          errors: [],
          items: [
            // {
            //   id: 1,
            //   name: "User 1"
            // }
          ]
        },
        permissionRead: true,
        permissionShare: false,
        permissionUpdate: false,
        permissionOwner: false,
      },
      shareForBoard: {
        board: {
          model: null,
          search: "",
          loading: false,
          errors: [],
          items: [
            // {
            //   id: 1,
            //   name: "Board A"
            // }
          ],
        },
        permissionRead: true,
        permissionShare: true,
        permissionUpdate: true,
        permissionOwner: true,
      }
    }),
    watch: {
      "shareForUser.user.search": function(){
        if(!this.preventUpdate){
          if(this.shareForUser.user.searchTimeout != null){
            clearTimeout(this.shareForUser.user.searchTimeout);
          }
          var that = this;
          this.shareForUser.user.searchTimeout = setTimeout(function(){
            that.InvokeUpdateUserAutocomplete();
          }, 500);
        }
        else{
          this.preventUpdate = false;
        }
      },
      "shareForUser.user.model": function(){
        this.preventUpdate = true;
      }
    },
    methods: {
      /**
       * Updates list of choices for User
       * @param search {string} Search string sent to defined API
       */
      APIUpdateUserAutocomplete(search){
        var updateId = ++this.shareForUser.user.currentUpdateId;
        this.shareForUser.user.loading = true;

        var that = this;
        axios({
          method: "GET",
          url: that.userSelectionAPI.url + `?search=${search}`,
          headers: that.userSelectionAPI.headers
        }).then((req) => {
          if(updateId == that.shareForUser.user.currentUpdateId){
            that.shareForUser.user.loading = false;
            var response = req.data;
            that.shareForUser.user.items = [];
            var tmp;
            for(var i = 0; i < response.length; i++){
              tmp = response[i];
              that.shareForUser.user.items.push({
                id: tmp.id,
                name: tmp.username + " (" + tmp.email + ")"
              });
            }
          }
        });
      },
      /**
       * Updates list of choices for Board
       * @param search {string} Search string sent to defined API
       */
      APIUpdateBoardAutocomplete(search){
        // TODO
        return search;
      },
      InvokeUpdateUserAutocomplete(){
        if(this.shareForUser.user.search != null && this.shareForUser.user.search != ""){
          this.APIUpdateUserAutocomplete(this.shareForUser.user.search);
        }
      },
      /**
       * Resets User choice to initial settings based on props
       */
      resetUserAutocomplete(){
        // Case: Use API to populate the choices list
        if(this.userSelectionUseAPI){
          // Initial list based on empty API call
          if(this.userSelectionAPILoadInitial){
            this.APIUpdateUserAutocomplete("");
          }
          // Initial list based on static choices list
          else if(this.userSelectionItems != null){
            this.shareForUser.user.items = this.userSelectionItems;
          }
          // Initial list is empty
          else{
            this.shareForUser.user.items = [];
          }
        }
        // Case: No API, static choices list
        else{
          if(this.userSelectionItems != null){
            this.shareForUser.user.items = this.userSelectionItems;
          }
          else{
            this.shareForUser.user.items = [];
          }
        }
      },
      /**
       * Resets Board choice to initial settings based on props
       */
      resetBoardAutocomplete(){
        // Case: Use API to populate the choices list
        if(this.boardSelectionUseAPI){
          // Initial list based on empty API call
          if(this.boardSelectionAPILoadInitial){
            this.APIUpdateBoardAutocomplete("");
          }
          // Initial list based on static choices list
          else if(this.boardSelectionItems != null){
            this.shareForBoard.board.items = this.boardSelectionItems;
          }
          // Initial list is empty
          else{
            this.shareForBoard.board.items = [];
          }
        }
        // Case: No API, static choices list
        else{
          if(this.boardSelectionItems != null){
            this.shareForBoard.board.items = this.boardSelectionItems;
          }
          else{
            this.shareForBoard.board.items = [];
          }
        }
      },
      resetUserPermissions(){
        this.shareForUser.permissionRead = this.defaultUserPermissionRead && this.allowPermissionRead;
        this.shareForUser.permissionShare = this.defaultUserPermissionShare && this.allowPermissionShare;
        this.shareForUser.permissionUpdate = this.defaultUserPermissionUpdate && this.allowPermissionUpdate;
        this.shareForUser.permissionOwner = this.defaultUserPermissionOwner && this.allowPermissionOwner;
      },
      resetBoardPermissions(){
        this.shareForBoard.permissionRead = this.defaultBoardPermissionRead && this.allowPermissionRead;
        this.shareForBoard.permissionShare = this.defaultBoardPermissionShare && this.allowPermissionShare;
        this.shareForBoard.permissionUpdate = this.defaultBoardPermissionUpdate && this.allowPermissionUpdate;
        this.shareForBoard.permissionOwner = this.defaultBoardPermissionOwner && this.allowPermissionOwner;
      },

      /**
       * Resets the dialog to the initial (default) settings
       */
      resetDialog(){
        this.resetUserAutocomplete();
        this.resetBoardAutocomplete();
        this.resetUserPermissions();
        this.resetBoardPermissions();

        this.tab = this.defaultTabDisplayed;
        this.disabled = false;
        this.loading = false;
      },

      open(resetDialog = true){
        if(resetDialog){
          this.resetDialog();
        }

        this.dialog = true;
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

      close(){
        this.dialog = false;
      },

      cancel(){
        this.close();
        this.$emit("cancelled");
      },

      confirm(){
        var data;
        this.globalError = null;
        // Share for USER
        if(this.tab == 0){
          if(this.shareForUser.permissionRead == false
            && this.shareForUser.permissionShare == false
            && this.shareForUser.permissionUpdate == false
            && this.shareForUser.permissionOwner == false
          ){
            this.globalError = "Wybierz przynajmniej jedno uprawnienie";
            return;
          }

          data = {
            shareFor: "USER",
            userId: this.shareForUser.user.model,
            permissionRead: this.shareForUser.permissionRead,
            permissionShare: this.shareForUser.permissionShare,
            permissionUpdate: this.shareForUser.permissionUpdate,
            permissionOwner: this.shareForUser.permissionOwner
          };
        }
        // Share for BOARD
        else {
          data = {
            shareFor: "BOARD",
            boardId: this.shareForBoard.board.model,
            permissionRead: this.shareForBoard.permissionRead,
            permissionShare: this.shareForBoard.permissionShare,
            permissionUpdate: this.shareForBoard.permissionUpdate,
            permissionOwner: this.shareForBoard.permissionOwner
          };
        }

        this.$emit("confirmed", data);
      },

      defaultSubmit(data, submitUrl, headers=null){
        this.startLoading();
        this.disable();

        if(headers == null){
          headers = {};
        }

        var that = this;
        if(data.shareFor == "USER"){
          return axios({
            url: submitUrl,
            method: "POST",
            headers: headers,
            data: {
              user_id: data.userId,
              permission_read: data.permissionRead,
              permission_share: data.permissionShare,
              permission_update: data.permissionUpdate,
              permission_owner: data.permissionOwner 
            }
          }).then((req) => {
            that.stopLoading();
            that.enable();
            var response = req.data;
            
            return {
              status: "OK",
              user: {
                id: response.user.id,
                username: response.user.username,
                firstName: response.user.first_name,
                lastName: response.user.last_name,
                email: response.user.email
              },
              passwordId: response.password.id,
              permissionRead: response.read,
              permissionShare: response.share,
              permissionUpdate: response.update,
              permissionOwner: response.owner
            };
          }).catch((error) => {
            that.stopLoading();
            that.enable();

            if(error.response){
              if(error.response.status == 403 || error.response.status == 401){
                that.globalError = "Odmowa dostępu";
              }
              else if(error.response.status == 400){
                if(error.response["__all__"] !== undefined && error.response["__all__"][0][0] == "User password assignment with this User and Password already exists."){
                  that.globalError = "Przypisanie już istnieje. Odśwież stronę.";
                }
                else if (error.response["user_id"] !== undefined && error.response["user_id"][0][0] == "User is password owner"){
                  that.globalError = "Użytkownik jest właścicielem hasła.";
                }
              }
              else if(error.response.status == 404){
                that.globalError = "Nie znaleziono hasła. Czy nie zostało usunięte?";
              }
              else if(error.response.status == 429){
                that.globalError = "Zapytanie zablokowane. Odczekaj minutę przed następną próbą.";
              }
            }
            else{
              that.globalError = "Błąd sieci. Spróbuj ponownie później.";
            }

            return {
              status: "ERR"
            };
          });
        }
        else{
          return null;
        }
      }
    }
  }
</script>