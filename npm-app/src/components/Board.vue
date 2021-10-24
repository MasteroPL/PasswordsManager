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
						>
							{{ item.username }}
						</div>
						<div class="board-desktop-right__item-div clickable"
							v-ripple
						>
							********
						</div>
						<div class="board-desktop-right__item-div clickable"
							v-ripple
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
		<v-dialog
			scrollable
			max-width="350px"
			v-model="passwordDetailsDialog.model"
		>
			<v-card>
				<v-card-title>Password details</v-card-title>

				<v-divider></v-divider>

				<v-list
				>
					<!-- Title -->
					<v-list-item>
						<v-list-item-content>
							<v-list-item-subtitle>TITLE</v-list-item-subtitle>
							<v-list-item-title>{{ passwordDetailsDialog.title }}</v-list-item-title>
						</v-list-item-content>
					</v-list-item>

					<!-- Username -->
					<v-list-item
						@click="onPasswordDialogUsernameCopyClick()"
						v-if="passwordDetailsDialog.username != null"
					>
						<v-list-item-content>
							<v-list-item-subtitle>USERNAME</v-list-item-subtitle>
							<v-list-item-title>{{ passwordDetailsDialog.username }}</v-list-item-title>
						</v-list-item-content>

						<v-list-item-action>
							<v-icon color="secondary"
								v-if="passwordDetailsDialog.usernameCopyTimeout == null"
							>mdi-content-copy</v-icon>
							<v-icon color="secondary"
								v-else
							>mdi-check</v-icon>
						</v-list-item-action>
					</v-list-item>

					<!-- Password -->
					<v-list-item
						:disabled="!permissionRead || passwordDetailsDialog.passwordCopyLoader"
						@click="onPasswordDialogPasswordCopyClick()"
					>
						<v-list-item-content>
							<v-list-item-subtitle>PASSWORD</v-list-item-subtitle>
							<v-list-item-title>********</v-list-item-title>
						</v-list-item-content>

						<v-list-item-action v-if="permissionRead">
							<v-progress-circular
								indeterminate
								:size="24"
								v-if="passwordDetailsDialog.passwordCopyLoader"
							></v-progress-circular>
							<v-icon color="secondary"
								v-else-if="passwordDetailsDialog.passwordCopyTimeout == null"
							>mdi-content-copy</v-icon>
							<v-icon color="secondary"
								v-else
							>mdi-check</v-icon>
						</v-list-item-action>
					</v-list-item>

					<!-- URL -->
					<v-list-item
						@click="onPasswordDialogUrlCopyClick()"
						v-if="passwordDetailsDialog.url != null"
					>
						<v-list-item-content>
							<v-list-item-subtitle>URL</v-list-item-subtitle>
							<v-list-item-title>{{ passwordDetailsDialog.url }}</v-list-item-title>
						</v-list-item-content>

						<v-list-item-action>
							<v-icon color="secondary"
								v-if="passwordDetailsDialog.urlCopyTimeout == null"
							>mdi-content-copy</v-icon>
							<v-icon color="secondary"
								v-else
							>mdi-check</v-icon>
						</v-list-item-action>
					</v-list-item>

					<!-- Notes -->
					<v-list-item
						v-if="passwordDetailsDialog.notes != null"
					>
						<v-list-item-content>
							<v-list-item-subtitle>NOTES</v-list-item-subtitle>
							<v-list-item-title class="board-details-dialog__notes" v-html="passwordDetailsDialog.notes"></v-list-item-title>
						</v-list-item-content>
					</v-list-item>
				</v-list>

				<v-divider></v-divider>

				<v-card-actions>
					<v-btn
						text
						color="red"
						v-if="permissionDelete"
					>
						Delete
					</v-btn>
					<v-spacer></v-spacer>
					<v-btn
						text
						@click="passwordDetailsDialog.model = false;"
					>
						Close
					</v-btn>
					<v-btn
						text
						color="secondary"
						v-if="permissionUpdate"
					>
						Edit
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

	</div>
</template>

<script>
var SURROGATE_PAIR_REGEXP = /[\uD800-\uDBFF][\uDC00-\uDFFF]/g,
    // Match everything outside of normal chars and " (quote character)
    NON_ALPHANUMERIC_REGEXP = /([^#-~| |!])/g;

export default {
	name: "Board",
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
				notes: "Sample notes with \na new line\nsome <b>html to spice things up</b>"
			},
			{
				id: -3,
				title: "Password 2",
				username: "User1234",
				url: "https://gooooooooogle.com",
				notes: "Sample notes with \na new line"
			},
			{
				id: -4,
				title: "Password 3",
				username: "User12345",
				url: null,
				notes: null
			},
			{
				id: -5,
				title: "Password 4",
				username: "User123456",
				url: null,
				notes: "Sample notes with \na new line"
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
		/**
		* Escapes all potentially dangerous characters, so that the
		* resulting string can be safely inserted into attribute or
		* element text.
		* @param value
		* @returns {string} escaped text
		*/
		encodeEntities(value) {
			return value.
				replace(/&/g, '&amp;').
				replace(SURROGATE_PAIR_REGEXP, function(value) {
					var hi = value.charCodeAt(0);
					var low = value.charCodeAt(1);
					return '&#' + (((hi - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000) + ';';
				}).
				replace(NON_ALPHANUMERIC_REGEXP, function(value) {
					return '&#' + value.charCodeAt(0) + ';';
				}).
				replace(/</g, '&lt;').
				replace(/>/g, '&gt;');
		},

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

			if(this.passwordDetailsDialog.usernameCopyTimeout != null){
				clearTimeout(this.passwordDetailsDialog.usernameCopyTimeout);
				this.passwordDetailsDialog.usernameCopyTimeout = null;
			}
			if(this.passwordDetailsDialog.passwordCopyTimeout != null){
				clearTimeout(this.passwordDetailsDialog.passwordCopyTimeout);
				this.passwordDetailsDialog.passwordCopyTimeout = null;
			}
			if(this.passwordDetailsDialog.urlCopyTimeout != null){
				this.passwordDetailsDialog.urlCopyTimeout = null;
			}
			this.passwordCopyLoader = false;

			if(passwordItem.notes != null){
				var notes = passwordItem.notes;
				notes = this.encodeEntities(notes);
				notes = notes.replace("&#10;", "<br />");
				this.passwordDetailsDialog.notes = notes;
			}
			else{
				this.passwordDetailsDialog.notes = null;
			}

			this.passwordDetailsDialog.model = true;
		},


		//
		// Event handlers
		//
		
		// Password Dialog
		onPasswordDialogUsernameCopyClick(){
			if (this.passwordDetailsDialog.usernameCopyTimeout != null){
				clearTimeout(this.passwordDetailsDialog.usernameCopyTimeout);
			}

			navigator.clipboard.writeText(this.passwordDetailsDialog.username);
			var that = this;
			this.passwordDetailsDialog.usernameCopyTimeout = setTimeout(function(){
				that.passwordDetailsDialog.usernameCopyTimeout = null;
			}, 750);
		},

		onPasswordDialogPasswordCopyClick(){
			if(this.passwordDetailsDialog.passwordCopyLoader){
				return;
			}

			if (this.passwordDetailsDialog.passwordCopyTimeout != null){
				clearTimeout(this.passwordDetailsDialog.passwordCopyTimeout);
				this.passwordDetailsDialog.passwordCopyTimeout = null;
			}

			var requestId = (++this.passwordDetailsDialog.requestId);

			this.passwordDetailsDialog.passwordCopyLoader = true;
			// TODO: download password
			// For now timeout to simulate
			var that = this;
			setTimeout(function(){
				if(requestId == that.passwordDetailsDialog.requestId){
					that.passwordDetailsDialog.passwordCopyLoader = false;
					
					navigator.clipboard.writeText("PASSWORD123!");
					that.passwordDetailsDialog.passwordCopyTimeout = setTimeout(function(){
						that.passwordDetailsDialog.passwordCopyTimeout = null;
					}, 750);
				}
			}, 2000);			
		},

		onPasswordDialogUrlCopyClick(){
			if (this.passwordDetailsDialog.urlCopyTimeout != null){
				clearTimeout(this.passwordDetailsDialog.urlCopyTimeout);
			}

			navigator.clipboard.writeText(this.passwordDetailsDialog.url);
			var that = this;
			this.passwordDetailsDialog.urlCopyTimeout = setTimeout(function(){
				that.passwordDetailsDialog.urlCopyTimeout = null;
			}, 750);
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

	.board-details-dialog__notes {
		white-space: normal;
		text-overflow: unset;
	}
</style>