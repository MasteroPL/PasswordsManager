<template>
  <v-container style="margin-bottom: 125px;">
    <new-password-dialog
      ref="newPasswordDialog"
      @confirmed="onNewPasswordDialogSubmit"
    ></new-password-dialog>

    <v-btn
      color="secondary"
      fab
      dark
      fixed
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

      @confirmed="onEditShareDialogSubmit"
      @delete="onEditShareDialogDeleteSubmit"
    ></edit-share-dialog>

    <edit-password-dialog
      ref="editPasswordDialog"
      :defaultTitle="editPasswordDialog.defaultTitle"
      :defaultDescription="editPasswordDialog.defaultDescription"
      @confirmed="onEditPasswordDialogSubmit"
    ></edit-password-dialog>

    <change-password-owner-dialog
      ref="changePasswordOwnerDialog"
      :userSelectionUseAPI="true"
      :userSelectionAPI="changePasswordOwnerDialog.userSelectionAPI"
      :userSelectionAPILoadInitial="changePasswordOwnerDialog.userSelectionAPILoadInitial"

      @confirmed="onChangePasswordOwnerDialogSubmit"
    ></change-password-owner-dialog>

    <!-- Dialog for completely removing a password from server memory -->
    <delete-password-dialog
      ref="deletePasswordDialog"
      @confirmed="onDeletePasswordDialogSubmit"
    ></delete-password-dialog>

    <!-- Dialog for removing a password from user account (other users will still see it) -->
    <remove-my-password-assignment-dialog
      ref="removeMyPasswordAssignmentDialog"
      @confirmed="onRemoveMyPasswordAssignmentDialogSubmit"
    ></remove-my-password-assignment-dialog>

    <v-data-table
      ref="datatable"
      :headers="dataTable.headers"
      :items="dataTable.items"
      :single-expand="false"
      :expanded.sync="dataTable.expanded"
      item-key="id"
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
          <td class="text-start truncate" style="width:30%; max-width: 310px;">{{ item.title }}</td>
          <td class="text-start truncate">{{ item.descriptionFull }}</td>
          <td class="text-start">
            <button v-if="!isExpanded" @click="expand(!isExpanded)" type="button" class="v-icon notranslate v-data-table__expand-icon v-icon--link mdi mdi-chevron-down"></button>
            <button v-else @click="expand(!isExpanded)" type="button" class="v-icon notranslate v-data-table__expand-icon v-icon--link mdi mdi-chevron-up"></button>
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
                  @click="openEditPasswordDialog(item)"
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

              <div class="title">{{ item.title }}</div>

              <div class="description" style="white-space:pre-wrap">{{ item.descriptionFull }}</div>

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
                    disabled
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
                    :disabled="!user.editable"
                    @click="(user.editable) ? openEditShareDialog(item, user) : null"
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
        userSelectionAPIUrlTemplate: appConfig.apiUrl + "api/password/{ID}/share/user/",
      },

      editShareDialog: {
        editedItem: null,
        editedShare: null,

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

      editPasswordDialog: {
        editedItem: null,

        defaultTitle: null,
        defaultDescription: null
      },

      changePasswordOwnerDialog: {
        editedItem: null,
        userSelectionAPILoadInitial: false,
        userSelectionAPI: {
          url: null,
          headers: {},
          data: {}
        },
        userSelectionAPIUrlTemplate: appConfig.apiUrl + "api/password/{ID}/change-owner/"
      },

      deletePasswordDialog: {
        editedItem: null
      },
      removeMyPasswordAssignmentDialog: {
        editedItem: null
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
        if(window.innerWidth < 600){
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
              name: item.owner.username + " (" + item.owner.email + ")"
            },
            sharedOnBoards: [],
            sharedWithUsers: []
          };

          for(var j = 0; j < item.assigned_users.length; j++){
            assignment = item.assigned_users[j];
            tmp.sharedWithUsers.push({
              id: assignment.user.id,
              name: assignment.user.username + " (" + assignment.user.email + ")",
              permissionRead: assignment.read,
              permissionShare: assignment.share,
              permissionUpdate: assignment.update,
              permissionOwner: assignment.owner,

              editable: assignment.editable
            });
          }

          result.push(tmp);
        }
        console.log(result);
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
                permissionOwner: feedback.permissionOwner,
                editable: true
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
        this.editShareDialog.editedItem = item;
        this.editShareDialog.editedShare = share;
        this.$nextTick(function() {
          that.$refs.editShareDialog.open();
        });
      },
      onEditShareDialogSubmit(data){
        var that = this;
        this.$refs.editShareDialog.defaultSubmit(
          data,
          this.editShareDialog.editedItem.id,
          this.editShareDialog.editedShare.id
        ).then((feedback) => {
          if(feedback.status == "OK"){
            that.$refs.editShareDialog.close();
            
            that.editShareDialog.editedShare.editable = true;
            that.editShareDialog.editedShare.permissionRead = feedback.data.read;
            that.editShareDialog.editedShare.permissionShare = feedback.data.share;
            that.editShareDialog.editedShare.permissionUpdate = feedback.data.update;
            that.editShareDialog.editedShare.permissionOwner = feedback.data.owner;

            that.editShareDialog.editedItem = null;
            that.editShareDialog.editedShare = null;
          }
        });
      },
      onEditShareDialogDeleteSubmit(){
        var that = this;
        this.$refs.editShareDialog.defaultDeleteSubmit(
          this.editShareDialog.editedItem.id,
          this.editShareDialog.editedShare.id
        ).then((feedback) => {
          if(feedback.status == "OK"){
            that.$refs.editShareDialog.close();
            
            var shares = that.editShareDialog.editedItem.sharedWithUsers;
            var tmp;
            for(var i = 0; i < shares.length; i++){
              tmp = shares[i];

              if(tmp == that.editShareDialog.editedShare){
                that.editShareDialog.editedItem.sharedWithUsers.splice(i, 1);
                break;
              }
            }

            that.editShareDialog.editedItem = null;
            that.editShareDialog.editedShare = null;
          }
        });
      },

      openEditPasswordDialog(item){
        this.editPasswordDialog.defaultTitle = item.title;
        this.editPasswordDialog.defaultDescription = item.descriptionFull;
        this.editPasswordDialog.editedItem = item;

        var that = this;
        this.$nextTick(function(){
          that.$refs.editPasswordDialog.open();
        });
      },
      onEditPasswordDialogSubmit(data){
        var that = this;
        this.$refs.editPasswordDialog.defaultSubmit(
          data,
          this.editPasswordDialog.editedItem.id
        ).then((feedback) => {
          if(feedback.status == "OK"){
            that.$refs.editPasswordDialog.close();
            that.editPasswordDialog.editedItem.title = feedback.data.title;

            that.editPasswordDialog.editedItem.descriptionShort = 
              (feedback.data.description.length > 100) 
                ? feedback.data.description.substring(0, 97) + "..." 
                : feedback.data.description
            ;
            that.editPasswordDialog.editedItem.descriptionFull = feedback.data.description;

            that.$nextTick(function(){
              that.$set(that.$refs.datatable.expanded, that.editPasswordDialog.editedItem.id, true);

              that.editPasswordDialog.editedItem = null;
            });
          }
        });
      },

      openChangePasswordOwnerDialog(item){
        var url = this.changePasswordOwnerDialog.userSelectionAPIUrlTemplate.replace("{ID}", item.id);
        this.changePasswordOwnerDialog.userSelectionAPI.url = url;
        this.changePasswordOwnerDialog.editedItem = item;
        
        this.$refs.changePasswordOwnerDialog.open();
      },
      onChangePasswordOwnerDialogSubmit(data){
        var that = this;
        this.$refs.changePasswordOwnerDialog.defaultSubmit(
          data.userId,
          this.changePasswordOwnerDialog.editedItem.id
        ).then((feedback) => {
          if(feedback.status == "OK"){
            var newOwner = feedback.data.password.owner;
            that.$refs.changePasswordOwnerDialog.close();

            that.changePasswordOwnerDialog.editedItem.ownedBy.id = newOwner.id;
            that.changePasswordOwnerDialog.editedItem.ownedBy.name = newOwner.username + " (" + newOwner.email + ")";
            that.changePasswordOwnerDialog.editedItem.isMyPassword = false;

            var shares = that.changePasswordOwnerDialog.editedItem.sharedWithUsers;
            var tmp;
            var toRemove = null;
            for(var i = 0; i < shares.length; i++){
              tmp = shares[i];
              // Removing assignment if user is the new main owner
              if(tmp.id == newOwner.id){
                toRemove = i;
              }
              else{
                if(tmp.permissionOwner){
                  tmp.editable = false;
                }
                else{
                  tmp.editable = true;
                }
              }
            }

            if(toRemove != null){
              that.changePasswordOwnerDialog.editedItem.sharedWithUsers.splice(toRemove, 1);
            }

            that.changePasswordOwnerDialog.editedItem = null;
          }
        });
      },

      openDeletePasswordDialog(item){
        this.deletePasswordDialog.editedItem = item;
        this.$refs.deletePasswordDialog.open();
      },
      onDeletePasswordDialogSubmit(){
        var that = this;
        this.$refs.deletePasswordDialog.defaultSubmit(
          this.deletePasswordDialog.editedItem.id
        ).then((feedback) => {
          if(feedback.status == "OK"){
            that.$refs.deletePasswordDialog.close();
            that.updateTable();
            that.deletePasswordDialog.editedItem = null;
          }
        });
      },

      openRemoveMyPasswordAssignmentDialog(item){
        this.removeMyPasswordAssignmentDialog.editedItem = item;
        this.$refs.removeMyPasswordAssignmentDialog.open();
      },
      onRemoveMyPasswordAssignmentDialogSubmit(){
        var that = this;
        this.$refs.removeMyPasswordAssignmentDialog.defaultSubmit(
          this.removeMyPasswordAssignmentDialog.editedItem.id
        ).then((feedback) => {
          if(feedback.status == "OK"){
            that.$refs.removeMyPasswordAssignmentDialog.close();
            that.updateTable();
            that.removeMyPasswordAssignmentDialog.editedItem = null;
          }
        });
      }
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

  .theme--light .passwords-list-item-details .non-editable-assignment {
    color: rgba(0, 0, 0, 0.5);
  }
  .theme--dark .passwords-list-item-details .non-editable-assignment {
    color: rgba(255, 255, 255, 0.5);
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