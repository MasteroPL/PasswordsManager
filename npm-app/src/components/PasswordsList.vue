<template>
  <v-container>
    <new-password-dialog
      ref="newPasswordDialog"
      @confirmed="onNewPasswordDialogSubmit"
    ></new-password-dialog>

    <v-btn
      color="secondary"
      fab
      dark
      style="position:fixed; bottom:40px; right: 40px;"
      @click="openNewPasswordDialog()"
    >
      <v-icon>mdi-plus</v-icon>
    </v-btn>

    <share-dialog
      ref="shareDialog"
      :allowPermissionRead="sharePasswordDialog.allowPermissionRead"
      :allowPermissionShare="sharePasswordDialog.allowPermissionShare"
      :allowPermissionUpdate="sharePasswordDialog.allowPermissionUpdate"
      :allowPermissionOwner="sharePasswordDialog.allowPermissionOwner"
      :userSelectionUseAPI="true"
      :userSelectionAPI="sharePasswordDialog.userSelectionAPI"
      :userSelectionAPILoadInitial="sharePasswordDialog.userSelectionAPILoadInitial"

      @confirmed="onShareDialogSubmit"
    ></share-dialog>

    <edit-share-dialog
      ref="editShareDialog"
      :usernameSlot="editShareDialog.usernameSlot"
      :allowPermissionRead="editShareDialog.allowPermissionRead"
      :allowPermissionShare="editShareDialog.allowPermissionShare"
      :allowPermissionUpdate="editShareDialog.allowPermissionUpdate"
      :allowPermissionOwner="editShareDialog.allowPermissionOwner"
      :defaultPermissionRead="editShareDialog.defaultPermissionRead"
      :defaultPermissionShare="editShareDialog.defaultPermissionShare"
      :defaultPermissionUpdate="editShareDialog.defaultPermissionUpdate"
      :defaultPermissionOwner="editShareDialog.defaultPermissionOwner"
    ></edit-share-dialog>

    <change-password-owner-dialog
      ref="changePasswordOwnerDialog"
      :userSelectionUseAPI="true"
      :userSelectionAPI="changePasswordOwnerDialog.userSelectionAPI"
      :userSelectionAPILoadInitial="changePasswordOwnerDialog.userSelectionAPILoadInitial"
    ></change-password-owner-dialog>

    <!-- Dialog for completely removing a password from server memory -->
    <delete-password-dialog
      ref="deletePasswordDialog"
    ></delete-password-dialog>

    <!-- Dialog for removing a password from user account (other users will still see it) -->
    <remove-my-password-assignment-dialog
      ref="removeMyPasswordAssignmentDialog"
    ></remove-my-password-assignment-dialog>

    <v-data-table
      :headers="dataTable.headers"
      :items="dataTable.items"
      :single-expand="true"
      :expanded.sync="dataTable.expanded"
      item-key="title"
      show-expand
      hide-default-footer

      :loading="dataTable.meta.loading"
      loading-text="Wczytywanie..."
    >
      <template v-slot:top>
        <v-toolbar flat>
          <v-toolbar-title>Wszystkie hasła</v-toolbar-title>
        </v-toolbar>
      </template>
      <template v-slot:item="{ item, expand, isExpanded }" v-if="dataTable.mode == 'DEFAULT'">
        <tr>
          <td class="text-start truncate">{{ item.title }}</td>
          <td class="text-start truncate" style="width:70%">{{ item.descriptionFull }}</td>
          <td class="text-start">
            <button @click="expand(!isExpanded)" type="button" class="v-icon notranslate v-data-table__expand-icon v-icon--link mdi mdi-chevron-down"></button>
          </td>
        </tr>
      </template>
      <template v-slot:expanded-item="{ headers, item }">
        <with-root v-bind:show="dataTable.mode == 'DEFAULT'">
          <tr>
            <td :colspan="headers.length" class="passwords-list-item-details">
              <div class="actions" style="text-align:right; padding-bottom: 15px;">
                <!-- Copy to clipboard -->
                <v-tooltip
                  bottom
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      icon
                      v-if="item.permissionRead || item.permissionOwner"
                      color="secondary"
                      :loading="item.copyButtonLoading"
                      @click="copyPassword(item)"
                      v-bind="attrs"
                      v-on="on"
                    >
                      <v-icon v-if="!item.copyButtonCopiedState">mdi-content-copy</v-icon>
                      <v-icon v-else>mdi-check</v-icon>
                    </v-btn>
                  </template>
                  <span v-if="!item.copyButtonCopiedState">Skopiuj hasło do schowka</span>
                  <span v-else>Hasło skopiowane do schowka</span>
                </v-tooltip>

                <!-- Share -->
                <v-btn
                  icon
                  v-if="item.permissionShare || item.permissionOwner"
                  color="secondary"
                  @click="openShareDialog(item)"
                >
                  <v-icon>mdi-share</v-icon>
                </v-btn>

                <!-- Update -->
                <v-btn
                  icon
                  v-if="item.permissionUpdate || item.permissionUpdate"
                  color="secondary"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>

                <!-- Change owner -->
                <v-btn
                  icon
                  color="secondary"
                  v-if="item.isMyPassword"
                  @click="openChangePasswordOwnerDialog(item)"
                >
                  <v-icon>mdi-star</v-icon>
                </v-btn>

                <!-- Delete -->
                <v-btn
                  icon
                  color="secondary"
                  v-if="item.isMyPassword"
                  @click="openDeletePasswordDialog(item)"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
                <v-btn
                  icon
                  color="secondary"
                  v-else
                  @click="openRemoveMyPasswordAssignmentDialog(item)"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </div>

              <div class="description">
                {{ item.descriptionFull }}
              </div>

              <v-list class="assignments">
                <!-- Information about the password owner -->
                <v-list-group
                  :value="true"
                  prepend-icon="mdi-star"
                  color="secondary"
                >
                  <template v-slot:activator>
                    <v-list-item-content>
                      <v-list-item-title>Utworzone przez</v-list-item-title>
                    </v-list-item-content>
                  </template>

                  <v-list-item
                    link
                  >
                    <v-list-item-title>{{ item.ownedBy.name }}</v-list-item-title>

                    <v-icon color="secondary" small>mdi-eye</v-icon>
                    <v-icon color="secondary" small>mdi-share</v-icon>              
                    <v-icon color="secondary" small>mdi-pencil</v-icon>
                    <v-icon color="secondary" small>mdi-star</v-icon>
                  </v-list-item>
                </v-list-group>

                <!-- Information (if provided by server) on which boards the password was shared -->
                <v-list-group
                  :value="false"
                  prepend-icon="mdi-account-multiple"
                  color="secondary"
                  v-if="item.sharedWithUsers.length > 0"
                >
                  <template v-slot:activator>
                    <v-list-item-content>
                      <v-list-item-title>Przypisani użytkownicy</v-list-item-title>
                    </v-list-item-content>
                  </template>

                  <v-list-item
                    v-for="(user) in item.sharedWithUsers"
                    :key="user.id" 
                    link
                    @click="openEditShareDialog(item, user)"
                  >
                    <v-list-item-title>{{ user.name }}</v-list-item-title>

                    <!-- Icons displays access a person has to passwords -->
                    <v-icon color="secondary" small v-if="user.permissionRead">mdi-eye</v-icon>
                    <v-icon small v-else>mdi-eye-off</v-icon>
                    <v-icon color="secondary" small v-if="user.permissionShare">mdi-share</v-icon>
                    <v-icon small v-else>mdi-share-off</v-icon>
                    <v-icon color="secondary" small v-if="user.permissionUpdate">mdi-pencil</v-icon>
                    <v-icon small v-else>mdi-pencil-off</v-icon>
                    <v-icon color="secondary" small v-if="user.permissionOwner">mdi-star</v-icon>
                    <v-icon small v-else>mdi-star-off</v-icon>
                  </v-list-item>
                </v-list-group>

                <!-- Information (if provided by server) with what users the password was shared -->
                <v-list-group
                  :value="false"
                  prepend-icon="mdi-view-dashboard"
                  color="secondary"
                  v-if="item.sharedOnBoards.length > 0"
                >
                  <template v-slot:activator>
                    <v-list-item-content>
                      <v-list-item-title>Przypisane tablice</v-list-item-title>
                    </v-list-item-content>
                  </template>

                  <v-list-item
                    v-for="(board) in item.sharedOnBoards"
                    :key="board.id" 
                    link
                  >
                    <v-list-item-title>{{ board.name }}</v-list-item-title>

                    <!-- Icons displays access a board has to passwords -->
                    <v-icon color="secondary" small v-if="board.permissionRead">mdi-eye</v-icon>
                    <v-icon small v-else>mdi-eye-off</v-icon>
                    <v-icon color="secondary" small v-if="board.permissionShare">mdi-share</v-icon>
                    <v-icon small v-else>mdi-share-off</v-icon>
                    <v-icon color="secondary" small v-if="board.permissionUpdate">mdi-pencil</v-icon>
                    <v-icon small v-else>mdi-pencil-off</v-icon>
                    <v-icon color="secondary" small v-if="board.permissionOwner">mdi-star</v-icon>
                    <v-icon small v-else>mdi-star-off</v-icon>
                  </v-list-item>
                </v-list-group>
              </v-list>
            </td>
          </tr>
        </with-root>
      </template>
    </v-data-table>
  </v-container>
</template>

<script>
  import appConfig from "../config"
  import axios from "axios"
  import copyToClipboard from "copy-to-clipboard"

  export default {
    name: 'PasswordsList',

    data: () => ({
      rsaTransferKey: null,
      sharePasswordDialog: {
        allowPermissionRead: true,
        allowPermissionShare: true,
        allowPermissionUpdate: true,
        allowPermissionOwner: true,
        userSelectionAPILoadInitial: false,
        userSelectionAPI: {
          url: null,
          headers: {},
          data: {}
        },
        editedItem: null,
        userSelectionAPIUrlTemplate: "https://localhost:8000/api/password/{ID}/share/user/",
      },

      editShareDialog: {
        usernameSlot: null,

        allowPermissionRead: true,
        allowPermissionShare: true,
        allowPermissionUpdate: true,
        allowPermissionOwner: true,
        defaultPermissionRead: false,
        defaultPermissionShare: false,
        defaultPermissionUpdate: false,
        defaultPermissionOwner: false
      },

      changePasswordOwnerDialog: {
        editedItem: null,
        userSelectionAPILoadInitial: false,
        userSelectionAPI: {
          url: null,
          headers: {},
          data: {}
        },
        userSelectionAPIUrlTemplate: "https://localhost:8000/api/password/{ID}/change-ownership/"
      },

      deletePasswordDialog: {
        editedId: null
      },
      removeMyPasswordAssignmentDialog: {
        editedId: null
      },

      dataTable: {
        mode: "DEFAULT",
        expanded: [],
        headers: [
          { text: 'Tytuł', value: 'title' },
          { text: 'Opis', value: 'descriptionShort' },
          { text: '', value: 'data-table-expand' }
        ],
        meta: {
          loading: false,
          page: 1,
          perPage: 10,
          search: '',
          totalPages: 0,
          currentUpdateId: 0,
          asc: true
        },
        items: [
          // {
          //   copyButtonLoading: false,    
          //
          //   // Display check mark instead of copy icon
          //   copyButtonCopiedState: false,
          //
          //   permissionRead: true,
          //   permissionShare: true,
          //   permissionUpdate: true,
          //   permissionOwner: true,
          //   isMainOwner: true,
          //   title: "Hasło XYZ",
          //   descriptionShort: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam commodo congue...",
          //   descriptionFull: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam commodo congue leo eu ultrices. Aliquam erat volutpat. Pellentesque laoreet mauris non ullamcorper pulvinar. Suspendisse egestas molestie purus tincidunt rhoncus. Fusce est ligula, imperdiet ac velit a, tempor tincidunt lectus. Aenean at augue sagittis, vulputate ante eget, vulputate mi. Pellentesque ligula lorem, ultrices eget rutrum at, dictum bibendum quam. Praesent elementum orci lacus, vel aliquam libero hendrerit eget. Cras ac velit tortor. Phasellus at metus euismod, varius velit ac, tempor arcu. Pellentesque ullamcorper, ligula ut venenatis dignissim, libero ipsum mollis ex, sed viverra nisi metus id lacus. Duis mattis rutrum ex, in cursus ligula elementum vulputate.",
          //   sharedOnBoards: [
          //     {
          //       id: 1,
          //       name: "Board A",
          //       permissionRead: true,
          //       permissionShare: false,
          //       permissionUpdate: true,
          //       permissionOwner: false
          //     }
          //   ],
          //   sharedWithUsers: [
          //     {
          //       id: 2,
          //       name: "sample_user1",
          //       permissionRead: false,
          //       permissionShare: true,
          //       permissionUpdate: false,
          //       permissionOwner: false
          //     }
          //   ],
          //   ownedBy: {
          //     id: 1,
          //     name: "admin"
          //   }
          // }
        ]
      }
    }),
    created(){
      window.addEventListener("resize", this.handleResize);
    },
    mounted(){
      this.handleResize();
      this.updateTable();
    },
    props: {
      userData: {
        type: Object,
        required: true
      }
    },
    methods: {
      handleResize(){
        if(window.innerWidth < 550){
          this.dataTable.mode = "MOBILE";
        }
        else{
          this.dataTable.mode = "DEFAULT";
        }
      },
      processRequestItems(items){
        this.items = [];
        var item;
        var assignment;
        var tmp;
        var result = [];
        for(var i = 0; i < items.length; i++){
          item = items[i];
          tmp = {
            copyButtonLoading: false,
            // Display check mark instead of copy icon
            copyButtonCopiedState: false,

            id: item.code,
            permissionRead: item.read,
            permissionShare: item.share,
            permissionUpdate: item.update,
            permissionOwner: item.is_owner,
            isMainOwner: this.userData.id == item.owner.id,
            title: item.title,
            descriptionShort: (item.description.length > 100) ? item.description.substring(0, 97) + "..." : item.description,
            descriptionFull: item.description,
            code: item.code,
            isMyPassword: item.owner.id == this.userData.id,
            ownedBy: {
              id: item.owner.id,
              name: item.owner.username
            },
            sharedOnBoards: [],
            sharedWithUsers: []
          };

          for(var j = 0; j < item.assigned_users.length; j++){
            assignment = item.assigned_users[j];
            tmp.sharedWithUsers.push({
              id: assignment.user.id,
              name: assignment.user.username,
              permissionRead: assignment.read,
              permissionShare: assignment.share,
              permissionUpdate: assignment.update,
              permissionOwner: assignment.owner,

              editable: true
            });
          }

          result.push(tmp);
        }
        return result;
      },

      updateTable(){
        var updateId = ++this.dataTable.meta.currentUpdateId;

        var url = appConfig.apiUrl + `api/passwords/?page=${this.dataTable.meta.page}&per_page=${this.dataTable.meta.perPage}&search=${this.dataTable.meta.search}&order_asc=${this.dataTable.meta.asc}`;
        this.dataTable.meta.loading = true;
        var that = this;

        axios({
          method: "GET",
          url: url
        }).then((req) => {
          if(updateId == that.dataTable.meta.currentUpdateId){
            var response = req.data;
            that.totalPages = response.num_Pages;
            
            that.dataTable.items = that.processRequestItems(response.items);
            console.log(that.dataTable.items);
          }
        }).finally(() => {
          this.dataTable.meta.loading = false;
        });

      },

      openShareDialog(password){
        if(password.isMainOwner){
          this.sharePasswordDialog.allowPermissionRead = true;
          this.sharePasswordDialog.allowPermissionShare = true;
          this.sharePasswordDialog.allowPermissionUpdate = true;
          this.sharePasswordDialog.allowPermissionOwner = true;
        }
        else if(password.permissionOwner){
          this.sharePasswordDialog.allowPermissionRead = true;
          this.sharePasswordDialog.allowPermissionShare = true;
          this.sharePasswordDialog.allowPermissionUpdate = true;
          this.sharePasswordDialog.allowPermissionOwner = false;
        }
        else if(password.permissionShare){
          this.sharePasswordDialog.allowPermissionRead = true;
          this.sharePasswordDialog.allowPermissionShare = false;
          this.sharePasswordDialog.allowPermissionUpdate = false;
          this.sharePasswordDialog.allowPermissionOwner = false;
        }
        else{
          return;
        }

        var url = this.sharePasswordDialog.userSelectionAPIUrlTemplate.replace("{ID}", password.id);
        this.sharePasswordDialog.userSelectionAPI.url = url;
        this.sharePasswordDialog.editedItem = password;
        
        this.$refs.shareDialog.open();
      },
      onShareDialogSubmit(data){
        if(data.shareFor == "USER"){
          console.log(data);
          var that = this;
          this.$refs.shareDialog.defaultSubmit(data, 
            this.sharePasswordDialog.userSelectionAPI.url
          ).then((feedback) => {
            if(feedback.status == "OK"){
              that.$refs.shareDialog.close();
              that.sharePasswordDialog.editedItem.sharedWithUsers.push({
                id: feedback.user.id,
                name: feedback.user.username,
                permissionRead: feedback.permissionRead,
                permissionShare: feedback.permissionShare,
                permissionUpdate: feedback.permissionUpdate,
                permissionOwner: feedback.permissionOwner
              });
            }
          });
        }
      },
      openNewPasswordDialog(){
        this.$refs.newPasswordDialog.open();
      },
      onNewPasswordDialogSubmit(data){
        var that = this;
        this.$refs.newPasswordDialog.defaultSubmit(
          data
        ).then((feedback) => {
          if(feedback.status == "OK"){
            that.$refs.newPasswordDialog.close();
            that.updateTable();
          }
        });
      },
      copyPassword(item){
        if(!item.copyButtonLoading && !item.copyButtonCopiedState){
          item.copyButtonLoading = true;
          var url = appConfig.apiUrl + `api/password/${item.id}/obtain/`;
          axios({
            method: "POST",
            url: url
          }).then((req) => {
            var response = req.data;
            var password = response.password;
            copyToClipboard(password);
            
            item.copyButtonCopiedState = true;
            setTimeout(function(){
              item.copyButtonCopiedState = false;
            }, 1000);
          }).finally(() => {
            item.copyButtonLoading = false;
          });
        }
      },

      openEditShareDialog(item, share){
        // Defining what is visible to editing user
        if(item.isMyPassword){
          this.editShareDialog.allowPermissionRead = true;
          this.editShareDialog.allowPermissionShare = true;
          this.editShareDialog.allowPermissionUpdate = true;
          this.editShareDialog.allowPermissionOwner = true;
        }
        else if(item.permissionOwner){
          this.editShareDialog.allowPermissionRead = true;
          this.editShareDialog.allowPermissionShare = true;
          this.editShareDialog.allowPermissionUpdate = true;
          this.editShareDialog.allowPermissionOwner = false;
        }
        else{
          this.editShareDialog.allowPermissionRead = true;
          this.editShareDialog.allowPermissionShare = false;
          this.editShareDialog.allowPermissionUpdate = false;
          this.editShareDialog.allowPermissionOwner = false;
        }

        // Defining defaults
        this.editShareDialog.defaultPermissionRead = share.permissionRead;
        this.editShareDialog.defaultPermissionShare = share.permissionShare;
        this.editShareDialog.defaultPermissionUpdate = share.permissionUpdate;
        this.editShareDialog.defaultPermissionOwner = share.permissionOwner;

        this.editShareDialog.usernameSlot = share.name;

        var that = this;
        this.$nextTick(function() {
          that.$refs.editShareDialog.open();
        });
      },

      openChangePasswordOwnerDialog(item){
        var url = this.changePasswordOwnerDialog.userSelectionAPIUrlTemplate.replace("{ID}", item.id);
        this.changePasswordOwnerDialog.userSelectionAPI.url = url;
        this.changePasswordOwnerDialog.editedItem = item;
        
        this.$refs.changePasswordOwnerDialog.open();
      },

      openDeletePasswordDialog(item){
        this.deletePasswordDialog.editedId = item.id;
        this.$refs.deletePasswordDialog.open();
      },

      openRemoveMyPasswordAssignmentDialog(item){
        this.removeMyPasswordAssignmentDialog.editedId = item.id;
        this.$refs.removeMyPasswordAssignmentDialog.open();
      },
    }
  }
</script>

<style>
  .truncate {
    max-width: 1px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .v-data-table > .v-data-table__wrapper tbody tr.v-data-table__expanded__content {
    box-shadow: none;
  }

  .passwords-list-item-details {
    padding-top: 10px !important;
    padding-bottom: 10px !important;
  }

  .theme--light .passwords-list-item-details {
    background-color: #F5F5F5;
  }
  .theme--dark .passwords-list-item-details {
    background-color: #252525;
  }

  .passwords-list-item-details > .description {
    text-align: justify;
    padding-bottom: 10px;
  }

  .passwords-list-item-details .theme--light.v-list.assignments {
    background: none;
  }
  .passwords-list-item-details .theme--dark.v-list.assignments {
    background: none;
  }
</style>