<template>
	<div class="board-container">

		<div class="board-header"
			:style="(isAdmin) ? 'max-width: calc(100% - 50px);' : 'max-width: calc(100% - 16px);'"
		>
			<div
				class="board-header__content"
			>
				<h2 class="board-header__ellipsis">{{ boardName }}</h2>
				<div class="board-header__ellipsis">Board</div>

				<div 
					class="board-header__admin-button-container"
					v-if="isAdmin"
				>
					<v-tooltip bottom>
						<template v-slot:activator="{ on, attrs }">
							<v-btn
								color="secondary"
								fab
								small
								icon
								class="board-header__admin-button"
								v-bind="attrs"
								v-on="on"
							>
								<v-icon>settings</v-icon>
							</v-btn>
						</template>
						<span>Administration Panel</span>
					</v-tooltip>
				</div>
			</div>
		</div>

		<v-btn
			fab
			color="secondary"
			dark
			class="board__add-action_button"
		>
			<v-icon>mdi-plus</v-icon>
		</v-btn>

		<!--
			Desktop view
		-->
		<div class="board-container-desktop">
			<!-- Left side -->
			<div class="board-desktop-left">
				<v-list
					rounded
					dense 
				>
					<v-subheader>GROUPS</v-subheader>

					<v-list-item-group
						color="primary"
						v-model="selectedGroupDesktop"
						mandatory
					>
						<v-list-item
							v-for="item in boardGroups"
							:key="item.id"
						>
							<v-list-item-content
							>
								<v-list-item-title>{{ item.name }}</v-list-item-title>
							</v-list-item-content>
						</v-list-item>
					</v-list-item-group>
				</v-list>

				<v-btn
					class="board-desktop-left__config-button"
					dark
					fab
					x-small
					icon
					color="secondary"
					v-if="isAdmin"
				>
					<v-icon>mdi-pencil</v-icon>
				</v-btn>
			</div>

			<!-- Right side -->
			<div class="board-desktop-right">
				<v-list
					dense
					style="padding-right: 8px;"
				>
					<v-list-item class="board-desktop-right__header"
						style="padding-left: 6px;"
					>
						<div class="board-desktop-right__header-div">Title</div>
						<div class="board-desktop-right__header-div">Username</div>
						<div class="board-desktop-right__header-div">Password</div>
						<div class="board-desktop-right__header-div">URL</div>
					</v-list-item>

					<v-divider></v-divider>

					<!--
						List of passwords will be here
					-->
					<v-list-item
						v-for="item in groupPasswords"
						class="board-desktop-right__item"
						:key="item.id"
						style="padding-left: 6px; padding-top: 3px; padding-bottom: 3px;"
					>
						<div class="board-desktop-right__item-div clickable"
							v-ripple
							@click="openPasswordDetailsDialog(item)"
						>
							{{ item.title }}
						</div>
						<div class="board-desktop-right__item-div clickable"
							v-ripple
							@click="onUsernameClick(item)"
						>
							{{ item.username }}
						</div>
						<div class="board-desktop-right__item-div clickable"
							v-ripple
							@click="onPasswordClick(item)"
						>
							<span v-if="!item.passwordLoader">************</span>
							<v-progress-linear v-else indeterminate
								style="margin-top: 15px;"
								color="secondary"
							></v-progress-linear>
						</div>
						<div class="board-desktop-right__item-div clickable"
							v-ripple
							@click="onUrlClick(item)"
						>
							{{ item.url }}
						</div>
					</v-list-item>
				</v-list>
			</div>
		</div>

		<!--
			Mobile view
		-->
		<div class="board-container-mobile">
			<v-select
				v-model="selectedGroupMobile"
				:items="boardGroups"
				label="Displayed group"
				item-value="id"
				item-text="name"
				class="board-mobile__group-select"
				:style="(isAdmin) ? 'width: calc(100% - 50px);' : 'width: 100%;'"
			></v-select>

			<v-btn
				class="board-mobile__group-edit-button"
				icon
				color="secondary"
			>
				<v-icon>mdi-pencil</v-icon>
			</v-btn>

			<!--
				Passwords display on mobile here
			-->

			<v-divider></v-divider>

			<v-list
				class="board-mobile__passwords-list"
			>
				<v-list-item
					v-for="item in groupPasswords"
					:key="item.id"
					@click="openPasswordDetailsDialog(item)"
				>
					<v-list-item-content :two-line="item.notes != null && item.notes != ''">
						<v-list-item-title>{{ item.title }}</v-list-item-title>
						<v-list-item-subtitle
							v-if="item.notes != null && item.notes != ''"
						>
							{{ item.notes }}
						</v-list-item-subtitle>
					</v-list-item-content>
				</v-list-item>
			</v-list>
		</div>


		<!--
			Popups / Dialogs section
		-->
		<GenericPasswordDetailsDialog
			ref="GenericPasswordDetailsDialog"

			:passwordId="passwordDetailsDialog.passwordId"
			:title="passwordDetailsDialog.title"
			:username="passwordDetailsDialog.username"
			:url="passwordDetailsDialog.url"
			:notes="passwordDetailsDialog.notes"
			:permissionRead="permissionRead"
			:permissionUpdate="permissionUpdate"
			:permissionDelete="permissionDelete"
		></GenericPasswordDetailsDialog>

		<v-snackbar
      v-model="copiedToClickboardSnackbar.model"
    >
      <v-icon small style="padding-right: 10px">mdi-check</v-icon> Value copied to clipboard

      <template v-slot:action="{ attrs }">
        <v-btn
          color="secondary"
          text
          v-bind="attrs"
          @click="copiedToClickboardSnackbar.model = false"
        >
          Ok
        </v-btn>
      </template>
    </v-snackbar>

	</div>
</template>

<script>

import GenericPasswordDetailsDialog from '@/generic/GenericPasswordDetailsDialog.vue'

export default {
	name: "Board",
	components: {
		"GenericPasswordDetailsDialog": GenericPasswordDetailsDialog
	},
	data: () => ({

		isAdmin: true,
		permissionRead: true,
		permissionUpdate: true,
		permissionCreate: true,
		permissionDelete: true,
		selectedGroupDesktop: 2,
		selectedGroupMobile: -1,
		selectedGroup: -1,
		boardName: "SampleBoard with very very very long name",

		passwordCopyInProgress: false,

		boardGroups: [
			{
				id: -2,
				name: "Group 1"
			},
			{
				id: -3,
				name: "Group 2"
			},
			// This one will always be added at the end
			{
				id: -1,
				name: "Not grouped"
			}
		],
		groupPasswords: [
			{
				id: -2,
				title: "Password 1",
				username: "User123",
				url: null,
				notes: "Sample notes with \na new line\nsome <b>html to spice things up</b>",
				passwordLoader: false
			},
			{
				id: -3,
				title: "Password 2",
				username: "User1234",
				url: "https://gooooooooogle.com",
				notes: "Sample notes with \na new line",
				passwordLoader: false
			},
			{
				id: -4,
				title: "Password 3",
				username: "User12345",
				url: null,
				notes: null,
				passwordLoader: false
			},
			{
				id: -5,
				title: "Password 4",
				username: "User123456",
				url: null,
				notes: "Sample notes with \na new line",
				passwordLoader: false
			}
		],
		passwordDetailsDialog: {
			passwordId: -1,
			model: false,
			requestId: 0, // allows to ignore cancelled requests

			title: "Test title",

			username: "User1",
			usernameCopyTimeout: null,

			url: "https://google.com",
			urlCopyTimeout: null,

			passwordCopyLoader: false,
			passwordCopyTimeout: null,

			notes: "My notes nalk fnalk snflksan klfnsalk fnklsanlk fnasklf nlkasn lkfnsalk fnklaswn flksa klfnasfn lksa<br />with multiple<br />lines"
		},
		copiedToClickboardSnackbar: {
			model: false,
			timeout: null
		}
	}),
	mounted() {
	},
	watch: {
		// Vuetify really does not want to cooperate with me,
		// which is why I manually update the model formats
		//
		// List group wants the selected index,
		// Select wants the selected id
		selectedGroup(newValue) {
			this.selectedGroupMobile = newValue;
			this.selectedGroupDesktop = this.getSelectedGroupDesktopById(newValue);
		},
		selectedGroupMobile(newValue){
			this.selectedGroupDesktop = this.getSelectedGroupDesktopById(newValue);
		},
		selectedGroupDesktop(newValue){
			this.selectedGroupMobile = this.boardGroups[newValue].id;
		}
	},
	methods: {
		

		getSelectedGroupDesktopById(id){
			for(let i = 0; i < this.boardGroups.length; i++){
				if (this.boardGroups[i].id == id){
					return i;
				}
			}
			return null;
		},

		openPasswordDetailsDialog(passwordItem){
			this.passwordDetailsDialog.passwordId = passwordItem.id;
			this.passwordDetailsDialog.title = passwordItem.title;
			this.passwordDetailsDialog.url = passwordItem.url;
			this.passwordDetailsDialog.notes = passwordItem.notes;

			this.$refs.GenericPasswordDetailsDialog.open();
		},


		//
		// Event handlers
		//
		onCopiedToClickboard(){
			var comp = this.copiedToClickboardSnackbar;
			if(comp.timeout != null){
				clearTimeout(comp.timeout);
				comp.model = false;
				comp.timeout = null;
			}

			this.$nextTick(function(){
				comp.model = true;
				comp.timeout = setTimeout(function(){
					comp.model = false;
					comp.timeout=  null;
				}, 2000);
			});
		},

		onUsernameClick(passwordItem){
			if(passwordItem.username == null || passwordItem.username == ''){
				return;
			}

			navigator.clipboard.writeText(passwordItem.username);
			this.onCopiedToClickboard();
		},
		onUrlClick(passwordItem){
			if(passwordItem.url == null || passwordItem.url == ''){
				return;
			}

			navigator.clipboard.writeText(passwordItem.url);
			this.onCopiedToClickboard();
		},
		onPasswordClick(passwordItem){
			console.log(passwordItem);
		}
	}
}

</script>

<style scoped>
	.board-header {
	}
	.board-header__content {
		padding-left: 16px;
		padding-right: 0;
		position: relative;
		
		max-width: 100%;
	}
	.board-header__ellipsis {
		max-width: 100%;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.board-header__admin-button-container {
		height: 55px;
		width: 50px;
		position: absolute;
		top: 0;
		right: -56px;

		/*display: flex;
		flex-direction: column;
		justify-content: center;*/
	}

	/**
	* DESKTOP CSS
	*/

	.board-container-desktop{
		display: grid;
		grid-gap: 0;
		grid-template-columns: 180px 1fr;
		padding-bottom: 88px;
	}

	@media screen and (max-width: 700px){
		.board-container-desktop{
			display: none;
		}
	}

	.board-desktop-left {
		position: relative;
	}

	.board-desktop-left__config-button {
		position: absolute;
		top: 10px;
		right: 10px;
	}

	.board-desktop-right__header, .board-desktop-right__item {
		display: grid;
		grid-row-gap: 0;
		grid-template-columns: 3fr 2fr 85px 1fr;
	}
	.board-desktop-right__header {
		font-size: 14px;
	}
	.board-desktop-right__header-div {
		padding-left: 10px;
	}
	.board-desktop-right__item {
		font-size: 12px;
		height: 100%;
	}
	.board-desktop-right__item-div{
		overflow: hidden;
		text-overflow: ellipsis;

		padding: 0 10px;
		line-height: 34px;
		height: 34px;
	}
	.board-desktop-right__item-div.clickable {
		cursor: pointer;
		transition: background-color 0.2s ease-in-out;
		border-radius: 10px;
		user-select: none;
	}
	.board-desktop-right__item-div.clickable:hover {
		background-color: rgba(0, 0, 0, 0.12);
	}
	.theme--dark .board-desktop-right__item-div.clickable:hover {
		background-color: rgba(255, 255, 255, 0.12);
	}


	/**
	* MOBILE CSS
	*/

	.board-container-mobile {
		display: none;
		position: relative;
		padding-bottom: 88px;
	}
	@media screen and (max-width: 700px){
		.board-container-mobile{
			display: block;
		}
	}

	.board-mobile__group-select {
		padding-left: 16px;
		padding-left: 16px;
		margin-top: 16px;
	}
	.board-mobile__group-edit-button{
		position: absolute;
		right: 4px;
		top: 8px;
	}

	.board-mobile__passwords-list {
		background: none;
		background-color: none;
	}

	/**
	* OTHER CSS
	*/ 

	.board__add-action_button {
		position: fixed;
		bottom: 16px;
		right: 16px;
	}

	.board-container-desktop .v-list-item::after {
		height: 0;
		min-height: 0;
	}

	.board-container-desktop .v-list {
		background: none;
		background-color: none;
	}
</style>