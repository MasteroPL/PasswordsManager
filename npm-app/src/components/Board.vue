<template>
	<div class="board-container" style="padding-top: 12px; height: 100%; display: flex; flex-direction: column">

		<div class="board-header"
			:style="(isAdmin) ? 'max-width: calc(100% - 50px);' : 'max-width: calc(100% - 16px);'"
		>
			<v-btn
				x-small
				text
				style="padding-left: 4px; margin-left: 10px; margin-bottom: 4px;"
				@click="onBackToBoardsClick()"
			><v-icon left style="margin-right:0">mdi-chevron-left</v-icon> Back to boards</v-btn>

			<!-- DISPLAYING DATA -->
			<div
				class="board-header__content"
				v-if="state==STATES.DEFAULT"
			>
				<h2 class="board-header__ellipsis">{{ boardName }}</h2>
				<div :class='(cropDescription) ? "board-header__description" : "board-header__description no-crop"'
					@click="onDescriptionClick()"
					:style="boardDescriptionStyle"
					ref="boardDescriptionDiv"
				>
						<template v-if="boardDescription != null">
							<span v-html="boardDescription"></span>
						</template>
						<template v-else>
							No description
						</template>
				</div>
				

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
								@click="onAdministrationPanelButtonClick()"
							>
								<v-icon>settings</v-icon>
							</v-btn>
						</template>
						<span>Administration Panel</span>
					</v-tooltip>
				</div>
			</div>

			<!-- SCREEN IS LOADING -->
			<div
				v-else
			>
				<v-skeleton-loader
					class="board__header-skeleton-loader"
					elevation='0'
					type="card-heading"
					style="margin-left: -4px; margin-top: -4px; height: 52px;"
				></v-skeleton-loader>

				<v-skeleton-loader
					style="padding-left: 12px; padding-right: 16px;"
					elevation='0'
					type="text"
				></v-skeleton-loader>
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

		<v-divider></v-divider>

		<!--
			Desktop view
		-->
		<div class="board-container-desktop"
			v-if="state == STATES.DEFAULT"
		>
			<!-- Left side -->
			<div class="board-desktop-left">
				<v-list
					rounded
					dense 
				>
					<v-subheader>TABS</v-subheader>

					<v-list-item-group
						color="primary"
						v-model="selectedGroupDesktop"
						mandatory
					>
						<v-list-item
							v-for="item in boardTabs"
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
					<template v-if="tabPasswords != null && tabPasswords.length > 0">
						<v-list-item
							v-for="item in tabPasswords"
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
					</template>

					<template v-else>
						<div style="text-align: left; width: 100%; padding: 16px; opacity: 0.8;">
							No passwords
						</div>
					</template>
				</v-list>
			</div>
		</div>

		<!--
			Mobile view
		-->
		<div class="board-container-mobile"
			v-if="state == STATES.DEFAULT"
		>
			<v-select
				v-model="selectedGroupMobile"
				:items="boardTabs"
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
					v-for="item in tabPasswords"
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
			:permissionRead="board != null && board.permissions.read"
			:permissionUpdate="board != null && board.permissions.update"
			:permissionDelete="board != null && board.permissions.delete"
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

		<!--
			LOADING
		-->
		<div style="flex: 1 1 auto;"
			v-if="state == STATES.LOADING"
		>
			<div style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center">
				<v-progress-circular
					style="text-align:center; margin: 0 auto;"
					:size="64"
					color="primary"
					indeterminate
				></v-progress-circular>
			</div>
		</div>
	</div>
</template>

<script>
import ERRORS from '@/consts/standardErrors'
import GenericPasswordDetailsDialog from '@/generic/GenericPasswordDetailsDialog.vue'

const STATES = {
	INITIAL: 0,
	DEFAULT: 1,
	LOADING: 2
};

export default {
	name: "Board",

	components: {
		"GenericPasswordDetailsDialog": GenericPasswordDetailsDialog
	},
	data: () => ({
		state: STATES.LOADING,
		isAdmin: false,
		
		selectedGroupDesktop: 0,
		selectedGroupMobile: null,
		selectedGroup: null,
		cropDescription: true,
		expandDescription: false, // Separate control for animation
		cropTimeout: null,
		boardDescriptionStyle: "cursor: pointer; max-height: 22.5px;",
		

		board: null, // {
		// 	boardName: "SampleBoard with very very very long name",
		// 	boardDescription: null,
		// 	permissionRead: true,
		// 	permissionUpdate: true,
		// 	permissionCreate: true,
		// 	permissionDelete: true,
		// },

		getDataTimeout: null,

		passwordCopyInProgress: false,

		boardTabs: [
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
		tabPasswords: [
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
	computed: {
		STATES: () => {
			return STATES;
		},

		boardName: function() {
			return (this.board != null)
				? this.board.name
				: "";
		},

		boardDescription: function() {
			return (this.board != null)
				? this.board.descriptionHTML
				: "";
		}
	},
	async mounted() {
		this.isMounted = true;
		await this.getData();
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
			this.selectedGroupMobile = this.boardTabs[newValue].id;
		}
	},
	methods: {
		
		adaptStoreData(){
			let board = this.$store.getters["board/getBoard"];

			if(board != null){
				this.board = board;
				this.isAdmin = board.permissions.admin;

				this.boardTabs = board.tabs;
				this.tabPasswords = [];

				this.selectedGroup = board.tabs[0].id;
			}
			else{
				this.board = null;
				this.tabPasswords = [];
				this.boardTabs = [];
				this.isAdmin = false;
			}

			console.log(board.tabs);
		},

		async getData(){
			var that = this;
			if(this.getDataTimeout != null){
				clearTimeout(this.getDataTimeout);
			}
			this.getDataTimeout = setTimeout(function(){
				that.state = STATES.LOADING;
				that.getDataTimeout = null;
			}, 200);

			console.log("TEST");

			let exception = false;
			try {
				await this.$store.dispatch("board/getData", {
					id: this.$route.params.board_id
				});
			} catch(error){
				exception = true;
				switch(error.type){
					case ERRORS.UNAUTHORIZED:
						this.$router.push("/login/");
						return;

					case ERRORS.FORBIDDEN:
						this.$router.push("/login/");
						return;

					default:
						console.log(error);
				}
			} finally {
				if(this.getDataTimeout != null){
					clearTimeout(this.getDataTimeout);
					this.getDataTimeout = null;
				}

				this.state = STATES.DEFAULT;
			}

			if(exception) {
				return;
			}

			this.adaptStoreData();
		},

		getSelectedGroupDesktopById(id){
			for(let i = 0; i < this.boardTabs.length; i++){
				if (this.boardTabs[i].id == id){
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
		onBackToBoardsClick(){
			this.$router.push("/boards/");
		},

		onDescriptionClick(){
			// This is a mess....
			// But it works ¯\_(ツ)_/¯
			//
			// Also I've just spent an hour perfecting expansion of cropped board description. A functionality perhaps 1% of users will care about.
			// Ah yes, an hour well spent

			if(this.cropTimeout != null){
				clearTimeout(this.cropTimeout);
				this.cropTimeout = null;
				this.cropDescription = false;
			}

			this.expandDescription = !this.expandDescription;

			if(!this.expandDescription){
				this.boardDescriptionStyle = `cursor: pointer; max-height: 22.5px`;
				var that = this;
				this.cropTimeout = setTimeout(function(){
					that.cropDescription = true;
					that.cropTimeout = null;
				}, 200);
			}
			else{
				let height = this.$refs.boardDescriptionDiv.scrollHeight;
				this.boardDescriptionStyle = `cursor: pointer; max-height: ${height}px`;
				this.cropDescription = false;
				this.$forceUpdate();
			}
		},

		onAdministrationPanelButtonClick(){
			this.$router.push("/board/" + this.$route.params.board_id + "/admin/");
		},

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

<style>
	.board__header-skeleton-loader > .v-skeleton-loader__bone {
		background-color: rgba(0,0,0,0) !important;
	}

	.board__header-skeleton-loader {

	}
</style>

<style scoped>
	.board-header {
		padding-bottom: 12px;
	}
	
	.board-header__description {
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
		max-width: 100%;
		max-height: 22.5px;

		transition: max-height 0.3s;
	}
	.board-header__description.no-crop {
		-webkit-line-clamp: unset;
		display: block;
		-webkit-box-orient: unset;
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
		top: 26px;
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