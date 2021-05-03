<template>
  <v-container>
    <v-data-table
      :headers="dataTable.headers"
      :items="dataTable.items"
      :single-expand="false"
      :expanded.sync="dataTable.expanded"
      item-key="title"
      show-expand
      hide-default-footer
    >
      <template v-slot:top>
        <v-toolbar flat>
          <v-toolbar-title>Wszystkie hasła</v-toolbar-title>
        </v-toolbar>
      </template>
      <template v-slot:expanded-item="{ headers, item }">
        <td :colspan="headers.length" class="passwords-list-item-details">
          <div class="actions" style="text-align:right; padding-bottom: 15px;">
            <!-- Copy to clipboard -->
            <v-btn
              icon
              v-if="item.permissionRead || item.permissionOwner"
              color="secondary"
            >
              <v-icon>mdi-content-copy</v-icon>
            </v-btn>

            <!-- Share -->
            <v-btn
              icon
              v-if="item.permissionShare || item.permissionOwner"
              color="secondary"
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

            <!-- Delete -->
            <v-btn
              icon
              color="secondary"
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
              color=""
            >
              <template v-slot:activator>
                <v-list-item-content>
                  <v-list-item-title>Utworzone przez</v-list-item-title>
                </v-list-item-content>
              </template>

              <v-list-item
                link
              >
                <v-list-item-title>{{ item.createdBy.name }}</v-list-item-title>

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
              color=""
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
              >
                <v-list-item-title>{{ user.name }}</v-list-item-title>

                <!-- Icons displays access a person has to passwords -->
                <v-icon color="secondary" small v-if="user.permissionRead">mdi-eye</v-icon>
                <v-icon small v-else>mdi-eye-off</v-icon>
                <v-icon color="secondary" small v-if="user.permissionShare">mdi-share</v-icon>
                <v-icon small v-else>mdi-share-off</v-icon>
                <v-icon color="secondary" small v-if="user.permissionUpdate">mdi-pencil</v-icon>
                <v-icon small v-else>mdi-pencil-off</v-icon>
                <v-icon color="secondary" small v-if="user.permissiionOwner">mdi-star</v-icon>
                <v-icon small v-else>mdi-star-off</v-icon>
              </v-list-item>
            </v-list-group>

            <!-- Information (if provided by server) with what users the password was shared -->
            <v-list-group
              :value="false"
              prepend-icon="mdi-view-dashboard"
              color=""
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
                <v-icon color="secondary" small v-if="board.permissiionOwner">mdi-star</v-icon>
                <v-icon small v-else>mdi-star-off</v-icon>
              </v-list-item>
            </v-list-group>
          </v-list>
        </td>
      </template>
    </v-data-table>
  </v-container>
</template>

<script>
  export default {
    name: 'PasswordsList',

    data: () => ({
      dataTable: {
        expanded: [],
        headers: [
          { text: 'Tytuł', value: 'title' },
          { text: 'Opis', value: 'descriptionShort' },
          { text: '', value: 'data-table-expand' }
        ],
        items: [
          {
            permissionRead: true,
            permissionShare: true,
            permissionUpdate: true,
            permissionOwner: true,
            title: "Hasło XYZ",
            descriptionShort: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam commodo congue...",
            descriptionFull: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam commodo congue leo eu ultrices. Aliquam erat volutpat. Pellentesque laoreet mauris non ullamcorper pulvinar. Suspendisse egestas molestie purus tincidunt rhoncus. Fusce est ligula, imperdiet ac velit a, tempor tincidunt lectus. Aenean at augue sagittis, vulputate ante eget, vulputate mi. Pellentesque ligula lorem, ultrices eget rutrum at, dictum bibendum quam. Praesent elementum orci lacus, vel aliquam libero hendrerit eget. Cras ac velit tortor. Phasellus at metus euismod, varius velit ac, tempor arcu. Pellentesque ullamcorper, ligula ut venenatis dignissim, libero ipsum mollis ex, sed viverra nisi metus id lacus. Duis mattis rutrum ex, in cursus ligula elementum vulputate.",
            sharedOnBoards: [
              {
                id: 1,
                name: "Board A",
                permissionRead: true,
                permissionShare: false,
                permissionUpdate: true,
                permissionOwner: false
              },
              {
                id: 2,
                name: "Board B",
                permissionRead: true,
                permissionShare: false,
                permissionUpdate: false,
                permissionOwner: false
              },
              {
                id: 3,
                name: "Board C",
                permissionRead: true,
                permissionShare: true,
                permissionUpdate: true,
                permissionOwner: true
              }
            ],
            sharedWithUsers: [
              {
                id: 2,
                name: "sample_user1",
                permissionRead: false,
                permissionShare: true,
                permissionUpdate: false,
                permissionOwner: false
              },
              {
                id: 3,
                name: "sample_user2",
                permissionRead: true,
                permissionShare: false,
                permissionUpdate: false,
                permissionOwner: false
              },
              {
                id: 4,
                name: "sample_user3",
                permissionRead: true,
                permissionShare: true,
                permissionUpdate: true,
                permissionOwner: true
              }
            ],
            createdBy: {
              id: 1,
              name: "admin"
            }
          }
        ]
      }
    }),
  }
</script>

<style>
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