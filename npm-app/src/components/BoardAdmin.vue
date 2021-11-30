<template>
	<div class="board-admin" style="height: 100%; padding-top: 8px; display: flex; flex-direction: column">
			
		<v-tabs
			v-model="tabsModel"
			background-color="transparent"
			style="height:48px; flex: unset;"
			next-icon="mdi-arrow-right-bold-box-outline"
			prev-icon="mdi-arrow-left-bold-box-outline"
			show-arrows
		>
			<div class="board-admin_tabs-button">
				<v-btn
					icon
					@click="onBackButtonClick()"
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
			<v-tab
				v-if="permissionOwner"
				key="DELETE"
				style="color:red"
			>
				Delete
			</v-tab>
		</v-tabs>

		<v-tabs-items v-model="tabsModel" style="flex: 1 1 auto; height: 100%;">
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
				style="height: 100%;"
			>
				<div style="max-width: 600px"
					v-if="state == STATES.DEFAULT"
				>
					<v-text-field
						:disabled="details.controlsDisabled"
						v-model="details.boardName.current"
						label="Board name"
						outlined
						style="margin-top: 16px; max-width: 400px;"
						@change="details.anyChanges = true"
						:maxlength="50"
						counter
					></v-text-field>

					<v-textarea
						:disabled="details.controlsDisabled"
						v-model="details.boardDescription.current"
						label="Board description"
						outlined
						style="max-width: 600px;"
						@change="details.anyChanges = true"
						:maxlength="1024"
						counter
					></v-textarea>

					<!--
						TODO: image select
						Maybe this lib? https://github.com/SeregPie/VuetifyImageInput#readme
					-->

					<div class="board-admin__board-owner-autocomplete-container">
						<v-autocomplete
							v-model="details.boardOwner.current"
							:items="details.boardOwner.choices"
							outlined
							item-text="name"
							item-value="id"
							label="Board owner"
							:disabled="!permissionOwner || details.boardOwner.disabled || details.controlsDisabled"
							style="max-width: 400px;"
							:appendIcon="(details.boardOwner.disabled) ? '' : '$dropdown'"
							@change="details.anyChanges = true"
						></v-autocomplete>

						<div v-if="permissionOwner && details.boardOwner.disabled">
							<v-tooltip bottom>
								<template v-slot:activator="{on, attrs}">
									<v-btn
										fab
										small
										:disabled="details.controlsDisabled"
										color="secondary"
										v-bind="attrs"
										v-on="on"
										@mouseenter="details.boardOwner.unlockerIcon = 'mdi-lock-open-variant'"
										@mouseleave="details.boardOwner.unlockerIcon = 'mdi-lock'"
										class="board-admin__board-owner-autocomplete-unlocker"
										@click="details.boardOwner.unlockOwnerDialog = true"
									>
										<v-icon>{{ details.boardOwner.unlockerIcon }}</v-icon>
									</v-btn>
								</template>

								<span>Unlock this field</span>
							</v-tooltip>
						</div>
					</div>

					<v-progress-linear
						:active="details.loading"
						indeterminate
						color="primary"
						style="margin-bottom: 24px;"
					></v-progress-linear>

					<v-row style="padding-left: 12px; padding-right: 12px; margin-top: 8px; margin-bottom: 8px;">
						<v-spacer></v-spacer>
						<v-btn
							style="margin-right: 8px;"
							:disabled="!details.anyChanges || details.controlsDisabled"
							@click="onDetailsCancelClick()"
						>Cancel</v-btn>
						<v-btn
							color="primary"
							:disabled="!details.anyChanges || details.controlsDisabled"
							@click="onSubmitDetails()"
						>Save</v-btn>
					</v-row>
				</div>

				<div v-if="state == STATES.LOADING"
					style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center"
				>
					<v-progress-circular
						style="text-align:center; margin: 0 auto;"
						:size="64"
						color="primary"
						indeterminate
					></v-progress-circular>
				</div>

				<v-dialog
					v-model="details.boardOwner.unlockOwnerDialog"
					width="300"
				>
					<v-card>
						<v-card-title>
							Unlock Board Owner field
						</v-card-title>

						<v-divider style="margin-bottom: 20px;"></v-divider>

						<v-card-text>
							Are you sure you want to unlock "Board Owner" field?
							<br /><br />
							<u><b>WARNING:</b></u>
							<br /> 
							If you change the owner of the board, you will not be able to undo it!
						</v-card-text>

						<v-divider></v-divider>

						<v-card-actions>
							<v-spacer></v-spacer>
							<v-btn
								text
								@click="details.boardOwner.unlockOwnerDialog = false;"
							>Cancel</v-btn>

							<v-btn
								color="red"
								text
								@click="details.boardOwner.unlockOwnerDialog = false; details.boardOwner.disabled = false;"
							>
								Unlock
							</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>
			</v-tab-item>

			<!-- 
				Board users section
				Basically a list of users assigned to the board
			-->
			<v-tab-item
				key="USERS"
				class="board-admin__tab-item"
				style="height: 100%;"
			>
				<div style="max-width: 600px;"
					v-if="state==STATES.DEFAULT"
				>
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

				<div v-if="state == STATES.LOADING"
					style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center"
				>
					<v-progress-circular
						style="text-align:center; margin: 0 auto;"
						:size="64"
						color="primary"
						indeterminate
					></v-progress-circular>
				</div>
			</v-tab-item>

			<v-tab-item
				key="DELETE"
				class="board-admin__tab-item"
				style="height:100%"
			>
				<div style="max-width: 600px;"
					v-if="state == STATES.DEFAULT"
				>
					Delete board or smth
				</div>

				<div v-if="state == STATES.LOADING"
					style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center"
				>
					<v-progress-circular
						style="text-align:center; margin: 0 auto;"
						:size="64"
						color="primary"
						indeterminate
					></v-progress-circular>
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
import ERRORS from "@/consts/standardErrors.js"

const STATES = {
	INITIAL: 0,
	DEFAULT: 1,
	LOADING: 2
};

export default {
	name: "BoardAdmin",

	components: {
		"GenericRemoveBoardUserDialog": GenericRemoveBoardUserDialog,
		"GenericEditBoardUserDialog": GenericEditBoardUserDialog
	},

	data: () => ({
		state: STATES.INITIAL,
		initialLoadTimeout: null,

		tabsModel: null,

		permissionOwner: true,

		details: {
			submitTimeout: null,
			controlsDisabled: false,
			loading: false,

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
				disabled: true,
				unlockerIcon: "mdi-lock",
				unlockOwnerDialog: false,
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

			items: [

			],

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
	computed: {
		STATES: function(){
			return STATES;
		}
	},
	beforeMount(){
		
	},
	async mounted(){
		this.loadData();
	},
	methods: {
		updateOwnerChoices(){
			let item = null;
			let obj = null;

			this.details.boardOwner.choices.splice(0, this.details.boardOwner.choices.length);
			for(let i = 0; i < this.users.items.length; i++){
				item = this.users.items[i];
				obj = {
					id: item.id,
					name: item.username + " (" + item.lastName + " " + item.firstName + ")"
				};
				this.details.boardOwner.choices.push(obj);
			}

			obj = {
				id: this.details.boardOwner.initial.id,
				name: this.details.boardOwner.initial.name
			};

			this.details.boardOwner.choices.push(obj);
		},

		createUsersDisplayList(){
			let item = null;
			let obj = null;
			let subt2;

			this.users.displayItems.splice(0, this.users.displayItems.length);
			for(let i = 0; i < this.users.items.length; i++){
				item = this.users.items[i];

				if(item.admin){
					subt2 = "<span style='color:red;'>Administrator</span>";
				}
				else{
					let arr = [];
					if (item.create) arr.push("Create");
					if (item.read) arr.push("Read");
					if (item.update) arr.push("Update");
					if (item.delete) arr.push("Delete");

					subt2 = arr.join(", ");
				}
				obj = {
					id: item.id,
					name: item.username,
					create: item.create,
					read: item.read,
					update: item.update,
					delete: item.delete,
					admin: item.admin,
					subtitle1: item.lastName + " " + item.firstName,
					subtitle2: subt2
				};

				this.users.displayItems.push(obj);
			}
		},

		assignData(boardData, adminData) {
			this.details.boardName.initial = boardData.name;
			this.details.boardName.current = boardData.name;
			this.details.boardDescription.initial = boardData.description;
			this.details.boardDescription.current = boardData.description;

			this.details.boardOwner.initial = {
				id: adminData.owner.id,
				name: adminData.owner.username + " (" + adminData.owner.lastName + " " + adminData.owner.firstName + ")"
			};
			this.details.boardOwner.current = adminData.owner.id;
			
			let item = null;
			let obj;
			this.users.items.splice(0, this.users.items.length);
			for(let i = 0; i < adminData.users.length; i++){
				item = adminData.users[i];
				obj = {
					id: item.id,
					username: item.username,
					firstName: item.firstName,
					lastName: item.lastName,
					admin: item.admin,
					create: item.create,
					read: item.read,
					update: item.update,
					delete: item.delete
				};

				this.users.items.push(obj);
			}

			this.createUsersDisplayList();
			this.updateOwnerChoices();
		},

		async loadData(allowCache=true){
			if(this.initialLoadTimeout != null){
				clearTimeout(this.initialLoadTimeout);
			}
			var that = this;
			this.initialLoadTimeout = setTimeout(function(){
				that.state = STATES.LOADING;
				this.initialLoadTimeout = null;
			}, 200);

			let data = null;
			try {
				data = await this.$store.dispatch('board/getAdminData', {
					id: this.$route.params.board_id,
					allowCache: allowCache
				});
			} catch(error){
				switch(error.type){
					case ERRORS.UNAUTHORIZED:
						this.$router.push("/login/");
						break;
					case ERRORS.FORBIDDEN:
						this.$router.push("/login/");
						break;
				}
				console.log(error);
				return;
			}

			if(this.initialLoadTimeout != null){
				clearTimeout(this.initialLoadTimeout);
				this.initialLoadTimeout = null;
			}

			this.assignData(data.board, data.admin);
			this.state = STATES.DEFAULT;

			this.details.anyChanges = false;
		},

		/**
		 * Event handlers - GLOBAL
		 */
		onBackButtonClick(){
			this.$router.push({
				name: 'board',
				params: { 
					board_id: this.$route.params.board_id
				}
			});
		},
		
		/**
		* Event handlers - DETAILS
		*/
		onDetailsCancelClick(){
			this.details.boardName.current = this.details.boardName.initial;
			this.details.boardDescription.current = this.details.boardDescription.initial;
			this.details.boardOwner.current = this.details.boardOwner.initial.id;

			this.details.anyChanges = false;
		},

		setNewDetailsInitialValues() {
			this.details.boardName.initial = this.details.boardName.current;
			this.details.boardDescription.initial = this.details.boardDescription.current;
			console.log("TEST");
			
			let boardOwnerInitial = null;
			for(let i = 0; i < this.details.boardOwner.choices.length; i++){
				if(this.details.boardOwner.choices[i].id == this.details.boardOwner.current){
					boardOwnerInitial = this.details.boardOwner.choices[i];
					break;
				}
			}

			if(boardOwnerInitial == null){
				// Reload screen, there is a storage data discrepency
				this.loadData(false);
				return;
			}
			else{
				this.details.boardOwner.initial = boardOwnerInitial;
			}

			this.details.anyChanges = false;
			this.details.boardOwner.disabled = true;
		},

		async onSubmitDetails(){
			let data = {
				id: this.$route.params.board_id
			};
			let anyChanges = false;

			if (this.details.boardName.current != this.details.boardName.initial) {
				data.name = this.details.boardName.current;
				anyChanges = true;
			}
			if(this.details.boardDescription.current != this.details.boardDescription.initial){
				data.description = this.details.boardDescription.current;
				anyChanges = true;
			}
			if(!this.details.boardOwner.disabled
				&& this.permissionOwner
				&& this.details.boardOwner.current != this.details.boardOwner.initial.id
			){
				data.ownerId = this.details.boardOwner.current;
				anyChanges = true;
			}

			if(anyChanges){
				let exception = false;

				this.details.controlsDisabled = true;
				if(this.details.submitTimeout != null){
					clearTimeout(this.details.submitTimeout);
				}
				var that = this;
				this.details.submitTimeout = setTimeout(function(){
					that.details.loading = true;
					that.details.submitTimeout = null;
				}, 200);

				try {
					await this.$store.dispatch("board/updateBoard", data)
				} catch(error){
					console.log(error);
					exception = true;
				} finally {
					console.log(this.details.submitTimeout);
					if(this.details.submitTimeout != null){
						clearTimeout(this.details.submitTimeout);
						this.details.submitTimeout = null;
					}
					this.details.controlsDisabled = false;
					this.details.loading = false;
				}

				if(exception) {
					return;
				}

				this.loadData(true); // reload data from Vuex cache
			}
			else {
				// No changes were made
				this.details.anyChanges = false;
				this.details.boardOwner.disabled = true;
			}
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

<style>
</style>

<style scoped>
.dont-keep-active:focus::before {
	opacity: 0 !important;
}

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

.board-admin__board-owner-autocomplete-container {
	position: relative;
	max-width: 400px;
}
.board-admin__board-owner-autocomplete-unlocker {
	position: absolute;
	top: 8px;
	right: 8px;
}
</style>