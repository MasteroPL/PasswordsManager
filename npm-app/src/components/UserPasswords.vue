<template>
	<div class="user-passwords-container" style="padding-top: 12px; height: 100%; display: flex; flex-direction: column">

		<div class="user-passwords-header"
			style="max-width: calc(100% - 16px);"
		>
			<!-- DISPLAYING DATA -->
			<div
				class="user-passwords-header__content"
			>
				<h2>My Passwords</h2>				
			</div>
		</div>

		<v-btn
			fab
			color="secondary"
			dark
			class="user-passwords__add-action_button"
			@click="onAddPasswordButtonClick()"
		>
			<v-icon>mdi-plus</v-icon>
		</v-btn>

		<v-divider></v-divider>

		<!--
			Desktop view
		-->
		<div class="user-passwords-container-desktop"
			v-if="state == STATES.DEFAULT"
		>
			<!-- Left side -->
			<div class="user-passwords-desktop-left">
				<v-list
					rounded
					dense 
				>
					<v-subheader>MY TABS</v-subheader>

					<v-list-item-group
						color="primary"
						v-model="selectedGroupDesktop"
						mandatory
					>
						<v-list-item
							v-for="item in userTabs"
							:key="item.id"
						>
							<v-list-item-content
							>
								<v-list-item-title>{{ item.name }}</v-list-item-title>
							</v-list-item-content>
						</v-list-item>

						<v-subheader>OTHER</v-subheader>

						<v-list-item
							:key="-1"
						>
							<v-list-item-content
							>
								<v-list-item-title>Shared to me</v-list-item-title>
							</v-list-item-content>
						</v-list-item>
					</v-list-item-group>
				</v-list>

				<v-btn
					class="user-passwords-desktop-left__config-button"
					dark
					fab
					x-small
					icon
					color="secondary"
					@click="onTabsAdminButtonClick()"
				>
					<v-icon>mdi-pencil</v-icon>
				</v-btn>
			</div>

			<!-- Right side -->
			<div class="user-passwords-desktop-right">
				<v-list
					dense
					style="padding-right: 8px;"
				>
					<v-list-item class="user-passwords-desktop-right__header"
						style="padding-left: 6px;"
					>
						<div class="user-passwords-desktop-right__header-div">Title</div>
						<div class="user-passwords-desktop-right__header-div">Username</div>
						<div class="user-passwords-desktop-right__header-div">Password</div>
						<div class="user-passwords-desktop-right__header-div">URL</div>
					</v-list-item>

					<v-divider></v-divider>

					<!--
						List of passwords will be here
					-->
					<template v-if="tabPasswords != null && tabPasswords.length > 0">
						<v-list-item
							v-for="item in tabPasswords"
							class="user-passwords-desktop-right__item"
							:key="item.id"
							style="padding-left: 6px; padding-top: 3px; padding-bottom: 3px;"
						>
							<div class="user-passwords-desktop-right__item-div clickable"
								v-ripple
								@click="openPasswordDetailsDialog(item)"
							>
								{{ item.title }}
							</div>
							<div class="user-passwords-desktop-right__item-div clickable"
								v-ripple
								@click="onUsernameClick(item)"
							>
								{{ item.username }}
							</div>
							<div class="user-passwords-desktop-right__item-div clickable"
								v-ripple
								@click="onPasswordClick(item)"
							>
								<span v-if="!item.passwordLoader">************</span>
								<v-progress-linear v-else indeterminate
									style="margin-top: 15px;"
									color="secondary"
								></v-progress-linear>
							</div>
							<div class="user-passwords-desktop-right__item-div clickable"
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
		<div class="user-passwords-container-mobile"
			v-if="state == STATES.DEFAULT"
		>
			<v-select
				v-model="selectedGroupMobile"
				:items="userTabsMobile"
				label="Displayed tab"
				item-value="id"
				item-text="name"
				class="user-passwords-mobile__group-select"
				style="width: calc(100% - 50px);"
			>
			</v-select>

			<v-btn
				class="user-passwords-mobile__group-edit-button"
				icon
				color="secondary"
				@click="onTabsAdminButtonClick()"
			>
				<v-icon>mdi-pencil</v-icon>
			</v-btn>

			<!--
				Passwords display on mobile here
			-->

			<v-divider></v-divider>

			<v-list
				class="user-passwords-mobile__passwords-list"
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

			:boardMode="false"
			:passwordId="passwordDetailsDialog.passwordId"
			:title="passwordDetailsDialog.title"
			:username="passwordDetailsDialog.username"
			:url="passwordDetailsDialog.url"
			:notes="passwordDetailsDialog.notes"
			:permissionRead="passwordDetailsDialog.permissionRead"
			:permissionUpdate="passwordDetailsDialog.permissionUpdate"
			:permissionDelete="passwordDetailsDialog.permissionDelete"

			@deleted="getData(true)"
		></GenericPasswordDetailsDialog>

	<v-snackbar
      v-model="copiedToClipboardSnackbar.model"
    >
      <v-icon small style="padding-right: 10px">mdi-check</v-icon> Value copied to clipboard

      <template v-slot:action="{ attrs }">
        <v-btn
          color="secondary"
          text
          v-bind="attrs"
          @click="copiedToClipboardSnackbar.model = false"
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

const MODES = {
	ADDING: 0,
	EDITING: 1
};

export default {
	name: "UserPasswords",

	components: {
		"GenericPasswordDetailsDialog": GenericPasswordDetailsDialog
	},
	data: () => ({
		state: STATES.INITIAL,
		
		selectedGroupDesktop: 0,
		selectedGroupMobile: null,
		selectedGroup: null,
		
		preventSelectAutoupdate: false,
		getDataTimeout: null,
		passwordCopyInProgress: false,

		userTabs: [],
		userTabsMobile: [],
		tabPasswords: [],

		sharedPasswords: [],

		passwordDetailsDialog: {
			passwordId: null,
			model: false,
			requestId: 0, // allows to ignore cancelled requests

			title: "",

			username: null,
			usernameCopyTimeout: null,

			url: null,
			urlCopyTimeout: null,

			passwordCopyLoader: false,
			passwordCopyTimeout: null,

			notes: null,

			permissionRead: true,
			permissionUpdate: true,
			permissionDelete: true
		},
		copiedToClipboardSnackbar: {
			model: false,
			timeout: null
		}
	}),
	computed: {
		STATES: () => {
			return STATES;
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
			if(!this.preventSelectAutoupdate){
				this.selectedGroupMobile = newValue;
				this.selectedGroupDesktop = this.getSelectedGroupDesktopById(newValue);
			}

			this.onSelectTabChange();
		},
		selectedGroupMobile(newValue){
			this.selectedGroupDesktop = this.getSelectedGroupDesktopById(newValue);
			this.preventSelectAutoupdate = true;
			this.selectedGroup = newValue;
			this.preventSelectAutoupdate = false;
		},
		selectedGroupDesktop(newValue){
			// Shared to me tab
			if (newValue == this.userTabs.length){
				this.selectedGroupMobile = -1;
				this.preventSelectAutoupdate = true;
				this.selectedGroup = -1;
				this.preventSelectAutoupdate = false;
			}
			else {
				this.selectedGroupMobile = this.userTabs[newValue].id;
				this.preventSelectAutoupdate = true;
				this.selectedGroup = this.userTabs[newValue].id;
				this.preventSelectAutoupdate = false;
			}
		}
	},
	methods: {
		
		loadTabPasswords(tabId){
			this.tabPasswords.splice(0, this.tabPasswords.length);
			let passwords = this.$store.getters["userPasswords/getTabById"](tabId);
			let owner = null;

			if(tabId != -1) {
				passwords = passwords.passwords;
				this.passwordDetailsDialog.permissionUpdate = true;
				this.passwordDetailsDialog.permissionDelete = true;
			}
			else{
				this.passwordDetailsDialog.permissionUpdate = false;
				this.passwordDetailsDialog.permissionDelete = false;
			}

			for(let i = 0; i < passwords.length; i++){
				if (tabId != -1){
					owner = passwords[i].owner;
				}

				this.tabPasswords.push({
					id: passwords[i].code,
					title: passwords[i].title,
					notes: passwords[i].description,
					username: passwords[i].username,
					url: passwords[i].url,
					owner: owner,
					passwordLoader: false,
					passwordLoaderTimeout: null
				});
			}
		},

		adaptStoreData(tabId = null){
			let userPasswords = this.$store.getters["userPasswords/getPasswords"];
			if(userPasswords != null){
				this.userTabs = [];
				this.userTabsMobile = [];
				if(tabId == null){
					tabId = userPasswords.tabs[0].id;
				}

				for(var i = 0; i < userPasswords.tabs.length; i++){
					let obj = {
						id: userPasswords.tabs[i].id,
						name: userPasswords.tabs[i].name
					};
					this.userTabs.push(obj);
					this.userTabsMobile.push(obj);
				}
				this.userTabsMobile.push({
					divider: true
				});
				this.userTabsMobile.push({
					id: -1,
					name: "Shared to me"
				});

				this.preventSelectAutoupdate = true;
				this.selectedGroup = tabId;
				this.preventSelectAutoupdate = false;
				this.loadTabPasswords(tabId);
			}
			else{
				this.tabPasswords = [];
				this.userTabs = [];
				this.sharedPasswords = [];
			}
		},

		async getData(allowCache=true){
			var that = this;
			if(this.getDataTimeout != null){
				clearTimeout(this.getDataTimeout);
			}
			this.getDataTimeout = setTimeout(function(){
				that.state = STATES.LOADING;
				that.getDataTimeout = null;
			}, 200);

			let exception = false;
			try {
				await this.$store.dispatch("userPasswords/getData", {
					allowCache: allowCache
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

		async onSubmitClick(){
			this.titleErrors.splice(0, this.titleErrors.length);
			this.passwordErrors.splice(0, this.passwordErrors.length);
			this.selectedTabErrors.splice(0, this.selectedTabErrors.length);
			let anyErr = false;

			if(this.title == null || this.title == ""){
				anyErr = true;
				this.titleErrors.push("This field is required");
			}
			if(this.selectedTab == null || this.selectedTab == ""){
				anyErr = true;
				this.selectedTabErrors.push("This field is required");
			}

			if(this.mode == MODES.ADDING){
				if(this.password == null || this.password == ""){
					anyErr = true;
					this.passwordErrors.push("This field is required");
				}
			}

			if(anyErr) return;

			var that = this;
			if(this.stateTimeout != null){
				clearTimeout(this.stateTimeout);
			}
			this.stateTimeout = setTimeout(function(){
				that.state = STATES.SAVING;
				that.stateTimeout = null;
			});

			if(this.mode == MODES.ADDING){
				await this.$store.dispatch("userPasswords/addPassword", {
					tabId: this.selectedTab,
					password: this.password,
					title: this.title,
					description: this.notes,
					url: this.url,
					username: this.username
				});

				this.$emit("added");
			}
			else {
				await this.$store.dispatch("userPasswords/updatePassword", {
					passwordCode: this.$route.params.password_id,
					tabId: this.selectedTab,
					password: (this.passwordUnlocked && this.password != null && this.password != '') ? this.password : undefined,
					title: this.title,
					description: this.notes,
					url: this.url,
					username: this.username
				});

				this.$emit("edited");
			}

			if(this.stateTimeout != null){
				clearTimeout(this.stateTimeout);
			}
			this.stateTimeout = null;
			this.state = STATES.DEFAULT;
			this.$router.push("/user-passwords/");
		},

		getSelectedGroupDesktopById(id){
			if(id == -1){
				return this.userTabs.length;
			}

			for(let i = 0; i < this.userTabs.length; i++){
				if (this.userTabs[i].id == id){
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
			this.passwordDetailsDialog.username = passwordItem.username;

			this.$nextTick(function(){
				this.$refs.GenericPasswordDetailsDialog.open();
			});
		},


		//
		// Event handlers
		//

		onTabsAdminButtonClick(){
			this.$router.push("/user-passwords/tabs/");
		},

		onCopiedToClipboard(){
			var comp = this.copiedToClipboardSnackbar;
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
			this.onCopiedToClipboard();
		},
		onUrlClick(passwordItem){
			if(passwordItem.url == null || passwordItem.url == ''){
				return;
			}

			navigator.clipboard.writeText(passwordItem.url);
			this.onCopiedToClipboard();
		},
		async onPasswordClick(passwordItem){
			if(passwordItem.passwordLoaderTimeout != null){
				clearTimeout(passwordItem.passwordLoaderTimeout);
			}
			passwordItem.passwordLoaderTimeout = setTimeout(function(){
				passwordItem.passwordLoader = true;
				passwordItem.passwordLoaderTimeout = null;
			}, 200);

			let passwordValue = await this.$store.dispatch("userPasswords/getPasswordValue", {
				passwordCode: passwordItem.id
			});

			if(passwordItem.passwordLoaderTimeout != null){
				clearTimeout(passwordItem.passwordLoaderTimeout);
			}
			passwordItem.passwordLoader = false;
			passwordItem.passwordLoaderTimeout = null;

			navigator.clipboard.writeText(passwordValue);
			this.onCopiedToClipboard();
		},

		onSelectTabChange(){
			this.loadTabPasswords(this.selectedGroup);
		},

		onAddPasswordButtonClick(){
			this.$router.push("/user-password/");
		}
	}
}

</script>

<style>
	.user-passwords__header-skeleton-loader > .v-skeleton-loader__bone {
		background-color: rgba(0,0,0,0) !important;
	}

	.user-passwords__header-skeleton-loader {

	}
</style>

<style scoped>
	.user-passwords-header {
		padding-bottom: 12px;
	}
	
	.user-passwords-header__description {
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
		max-width: 100%;
		max-height: 22.5px;

		transition: max-height 0.3s;
	}
	.user-passwords-header__description.no-crop {
		-webkit-line-clamp: unset;
		display: block;
		-webkit-box-orient: unset;
	}

	.user-passwords-header__content {
		padding-left: 16px;
		padding-right: 0;
		position: relative;
		padding-top: 4px;
		
		max-width: 100%;
	}
	.user-passwords-header__ellipsis {
		max-width: 100%;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.user-passwords-header__admin-button-container {
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

	.user-passwords-container-desktop{
		display: grid;
		grid-gap: 0;
		grid-template-columns: 180px 1fr;
		padding-bottom: 88px;
	}

	@media screen and (max-width: 700px){
		.user-passwords-container-desktop{
			display: none;
		}
	}

	.user-passwords-desktop-left {
		position: relative;
	}

	.user-passwords-desktop-left__config-button {
		position: absolute;
		top: 10px;
		right: 10px;
	}

	.user-passwords-desktop-right__header, .user-passwords-desktop-right__item {
		display: grid;
		grid-row-gap: 0;
		grid-template-columns: 3fr 2fr 85px 1fr;
	}
	.user-passwords-desktop-right__header {
		font-size: 14px;
	}
	.user-passwords-desktop-right__header-div {
		padding-left: 10px;
	}
	.user-passwords-desktop-right__item {
		font-size: 12px;
		height: 100%;
	}
	.user-passwords-desktop-right__item-div{
		overflow: hidden;
		text-overflow: ellipsis;

		padding: 0 10px;
		line-height: 34px;
		height: 34px;
	}
	.user-passwords-desktop-right__item-div.clickable {
		cursor: pointer;
		transition: background-color 0.2s ease-in-out;
		border-radius: 10px;
		user-select: none;
	}
	.user-passwords-desktop-right__item-div.clickable:hover {
		background-color: rgba(0, 0, 0, 0.12);
	}
	.theme--dark .user-passwords-desktop-right__item-div.clickable:hover {
		background-color: rgba(255, 255, 255, 0.12);
	}


	/**
	* MOBILE CSS
	*/

	.user-passwords-container-mobile {
		display: none;
		position: relative;
		padding-bottom: 88px;
	}
	@media screen and (max-width: 700px){
		.user-passwords-container-mobile{
			display: block;
		}
	}

	.user-passwords-mobile__group-select {
		padding-left: 16px;
		padding-left: 16px;
		margin-top: 16px;
	}
	.user-passwords-mobile__group-edit-button{
		position: absolute;
		right: 4px;
		top: 26px;
	}

	.user-passwords-mobile__passwords-list {
		background: none;
		background-color: none;
	}

	/**
	* OTHER CSS
	*/ 

	.user-passwords__add-action_button {
		position: fixed;
		bottom: 16px;
		right: 16px;
	}

	.user-passwords-container-desktop .v-list-item::after {
		height: 0;
		min-height: 0;
	}

	.user-passwords-container-desktop .v-list {
		background: none;
		background-color: none;
	}
</style>