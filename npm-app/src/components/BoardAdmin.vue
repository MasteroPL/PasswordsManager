<template>
	<div class="board-admin">
		<v-tabs
			v-model="tabsModel"
			background-color="transparent"
			style="margin-top: 8px;"
		>
			<div class="board-admin_tabs-button">
				<v-btn
					icon
				>
					<v-icon>mdi-chevron-left</v-icon>
				</v-btn>
			</div>

			<v-tab
				key="DETAILS"
			>
				Details
			</v-tab>
			<v-tab
				key="USERS"
			>
				Users
			</v-tab>
		</v-tabs>

		<v-tabs-items v-model="tabsModel">
			<!-- 
				Board details section:
				* Board name
				* Description
				* Board image
				* Board owner
			-->
			<v-tab-item
				key="DETAILS"
				class="board-admin__tab-item"
			>
				<div style="max-width: 600px">
					<v-text-field
						v-model="details.boardName.current"
						label="Board name"
						outlined
						style="margin-top: 16px; max-width: 400px;"
						@change="details.anyChanges = true"
					></v-text-field>

					<v-textarea
						v-model="details.boardDescription.current"
						label="Board description"
						outlined
						style="max-width: 600px;"
						@change="details.anyChanges = true"
					></v-textarea>

					<!--
						TODO: image select
						Maybe this lib? https://github.com/SeregPie/VuetifyImageInput#readme
					-->

					<v-autocomplete
						v-model="details.boardOwner.current"
						:items="details.boardOwner.choices"
						outlined
						item-text="name"
						item-value="id"
						label="Board owner"
						:disabled="!permissionOwner"
						style="max-width: 400px;"
						@change="details.anyChanges = true"
					></v-autocomplete>

					<v-row style="padding-left: 12px; padding-right: 12px; margin-top: 8px; margin-bottom: 8px;">
						<v-spacer></v-spacer>
						<v-btn
							style="margin-right: 8px;"
							:disabled="!details.anyChanges"
							@click="onDetailsCancelClick()"
						>Cancel</v-btn>
						<v-btn
							color="primary"
							:disabled="!details.anyChanges"
						>Save</v-btn>
					</v-row>
				</div>
			</v-tab-item>

			<!-- 
				Board users section
				Basically a list of users assigned to the board
			-->
			<v-tab-item
				key="USERS"
				class="board-admin__tab-item"
			>
				<div style="max-width: 600px;">
					<v-row style="margin-top: 12px; margin-right: 0">
						<v-spacer></v-spacer>
						<v-btn
							color="primary"
							@click="onUserAddClick()"
						>
							Add user
							<v-icon
								right
								dark
							>mdi-plus</v-icon>
						</v-btn>
					</v-row>

					<v-list
						class="board-admin__users-list"
					>
						<template v-for="item in users.displayItems">
							<v-list-item
								
								:key="item.id"
							>
								<v-list-item-content>
									<v-list-item-title>{{ item.name }}</v-list-item-title>
									<v-list-item-subtitle>{{ item.subtitle1 }}</v-list-item-subtitle>
									<v-list-item-subtitle v-html="item.subtitle2"></v-list-item-subtitle>
								</v-list-item-content>

								<v-list-item-action
									v-if="!item.admin || permissionOwner"
								>
									<v-btn
										icon
										color="secondary"
										@click="onUserEditClick(item)"
									>
										<v-icon>mdi-pencil</v-icon>
									</v-btn>
								</v-list-item-action>
								<v-list-item-action style="margin-left: 0" v-if="!item.admin || permissionOwner">
									<v-btn
										icon
										color="red"
										@click="onUserRemoveClick(item)"
									>
										<v-icon>mdi-delete</v-icon>
									</v-btn>
								</v-list-item-action>
							</v-list-item>

							<v-divider 
								:key="'divider-' + item.id" 
								v-if="item.id != users.displayItems[users.displayItems.length - 1].id">
							</v-divider>
						</template>
					</v-list>
				</div>
			</v-tab-item>
		</v-tabs-items>

		<GenericRemoveBoardUserDialog
			ref="GenericRemoveBoardUserDialog"
			:userId="users.removeDialog.userId"
			:boardId="parseInt($route.params.board_id)"
			:userDisplayName="users.removeDialog.userDisplayName"
		></GenericRemoveBoardUserDialog>

		<GenericEditBoardUserDialog
			ref="GenericEditBoardUserDialog"
			:userId="users.editDialog.userId"
			:boardId="parseInt($route.params.board_id)"

			:canAddAdministrators="permissionOwner"
			:administrator="users.editDialog.administrator"
			:permissionCreate="users.editDialog.create"
			:permissionRead="users.editDialog.read"
			:permissionUpdate="users.editDialog.update"
			:permissionDelete="users.editDialog.delete"
		></GenericEditBoardUserDialog>
	</div>
</template>

<script>
import GenericRemoveBoardUserDialog from "@/generic/GenericRemoveBoardUserDialog.vue"
import GenericEditBoardUserDialog from "@/generic/GenericEditBoardUserDialog.vue"

export default {
	name: "BoardAdmin",

	components: {
		"GenericRemoveBoardUserDialog": GenericRemoveBoardUserDialog,
		"GenericEditBoardUserDialog": GenericEditBoardUserDialog
	},

	data: () => ({
		tabsModel: null,

		permissionOwner: true,

		details: {
			anyChanges: false,
			boardName: {
				initial: null,
				current: null
			},
			boardDescription: {
				initial: null,
				current: null
			},
			boardImage: null,
			boardOwner: {
				initial: {
					id: 0,
					name: "Jan Kowalski"
				},
				current: 0,
				choices: [
					{
						id: 0,
						name: "Jan Kowalski"
					},
					{
						id: -2,
						name: "Andrzej Kowalski"
					},
					{
						id: -3,
						name: "Karolina Kowalska"
					}
				]
			}
		},
		users: {
			removeDialog: {
				userId: -2,
				userDisplayName: "andrzej.kowalski (Kowalski Andrzej)" 
			},
			editDialog: {
				userId: null,
				administrator: false,
				create: false,
				read: false,
				update: false,
				delete: false
			},

			displayItems: [
				{
					id: -2,
					name: "andrzej.kowalski",
					create: false,
					read: true,
					update: false,
					delete: false,
					admin: false,
					subtitle1: "Kowalski Andrzej",
					subtitle2: "Read"
				},
				{
					id: -3,
					name: "karolina.kowalska",
					create: true,
					read: true,
					update: true,
					delete: true,
					admin: true,
					subtitle1: "Kowalska Karolina",
					subtitle2: "<span style='color:red;'>Administrator</span>"
				}
			]
		}
	}),
	beforeMount(){
		
	},
	mounted(){
	},
	methods: {
		
		/**
		* Event handlers - DETAILS
		*/
		onDetailsCancelClick(){
			this.details.boardName.current = this.details.boardName.initial;
			this.details.boardDescription.current = this.details.boardDescription.initial;
			this.details.boardOwner.current = this.details.boardOwner.initial.id;

			this.details.anyChanges = false;
		},


		/**
		* Event handlers - USERS
		*/
		onUserRemoveClick(item){
			this.users.removeDialog.userId = item.id;
			this.users.removeDialog.userDisplayName = `${item.name} (${item.subtitle1})`;
			this.$refs.GenericRemoveBoardUserDialog.open();
		},

		onUserAddClick(){
			this.users.editDialog.userId = null;
			this.users.editDialog.administrator = false;
			this.users.editDialog.create = false;
			this.users.editDialog.read = true;
			this.users.editDialog.update = false;
			this.users.editDialog.delete = false;

			this.$refs.GenericEditBoardUserDialog.open();
		},

		onUserEditClick(item){
			this.users.editDialog.userId = item.id;
			this.users.editDialog.administrator = item.admin;
			if(!item.admin){
				this.users.editDialog.create = item.create;
				this.users.editDialog.read = item.read;
				this.users.editDialog.update = item.update;
				this.users.editDialog.delete = item.delete;
			}
			else{
				this.users.editDialog.create = true;
				this.users.editDialog.read = true;
				this.users.editDialog.update = true;
				this.users.editDialog.delete = true;
			}

			this.$refs.GenericEditBoardUserDialog.open();
		},
	}
}
</script>

<style scoped>
.board-admin {
	max-width: 1024px;
	padding-left: 8px;
	padding-right: 8px;
}

.v-tabs-items {
	background-color: unset;
	padding: 8px;
}

.board-admin_tabs-button {
	display: flex;
	flex-direction: column;
	justify-content: center;
}

.board-admin__users-list {
	background: none;
	background-color: none;
	margin-top: 16px;
}
</style>