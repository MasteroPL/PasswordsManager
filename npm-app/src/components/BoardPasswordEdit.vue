<template>
	<div class="board-password-edit-container" style="padding-top: 12px; height: 100%; display: flex; flex-direction: column; padding-left: 8px; padding-right: 8px; max-width: 600px;">
		<div class="board-groups-edit__back">
			<v-btn
				text
				style="padding-left: 4px;"
				@click="onBackClick()"
			>
				<v-icon>mdi-chevron-left</v-icon>
				Back
			</v-btn>
		</div>

		<div v-if="state == STATES.DEFAULT || state == STATES.SAVING" style="padding: 0 12px;">
			<h2 style="margin-top: 8px; margin-bottom: 16px;">
				<span v-if="mode == MODES.ADDING">New password</span>
				<span v-if="mode == MODES.EDITING">Edit password</span>
			</h2>

			<v-text-field
				v-model="title"
				label="Title*"
				outlined
				style="max-width: 400px"
				:disabled="state != STATES.DEFAULT"
				:error-messages="titleErrors"

				:maxlength="50"
				counter
			></v-text-field>

			<div class="board-password-edit__password-cotnainer" style="position: relative">
				<v-text-field
					v-model="password"
					:type="passwordShow ? 'text' : 'password'"
					:append-icon="passwordUnlocked ? (passwordShow ? 'mdi-eye' : 'mdi-eye-off') : ''"
					:label="'password' + ((mode == MODES.ADDING) ? '*' : '')"
					outlined
					:disabled="!passwordUnlocked"
					:error-messages="passwordErrors"

					:maxlength="128"
					:counter="passwordUnlocked"
					@click:append="passwordShow = !passwordShow"
				></v-text-field>

				<v-tooltip bottom v-if="!passwordUnlocked">
					<template v-slot:activator="{on, attrs}">
						<v-btn
							fab
							small
							color="secondary"
							v-bind="attrs"
							v-on="on"
							@mouseenter="unlockIcon = 'mdi-lock-open-variant'"
							@mouseleave="unlockIcon = 'mdi-lock'"
							@click="unlockPasswordDialog = true"
							style="position: absolute; top: 8px; right: 8px"
						>
							<v-icon>{{ unlockIcon }}</v-icon>
						</v-btn>
					</template>

					<span>Unlock this field</span>
				</v-tooltip>
			</div>

			<v-dialog
				v-model="unlockPasswordDialog"
				width="300"
			>
				<v-card>
					<v-card-title>
						Unlock password field
					</v-card-title>

					<v-divider style="margin-bottom: 20px;"></v-divider>

					<v-card-text>
						Are you sure you want to unlock "Password" field?
					</v-card-text>

					<v-divider></v-divider>

					<v-card-actions>
						<v-spacer></v-spacer>
						<v-btn
							text
							@click="unlockPasswordDialog = false;"
						>Cancel</v-btn>

						<v-btn
							color="secondary"
							text
							@click="unlockPasswordDialog = false; password = null; passwordShow = false; passwordUnlocked = true;"
						>
							Unlock
						</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-select
				v-model="selectedTab"
				:items="tabs"
				item-text="name"
				item-value="id"
				label="Password tab*"
				style="max-width: 350px"
				outlined
				:disabled="state != STATES.DEFAULT"

				:error-messages="selectedTabErrors"
			></v-select>

			<v-text-field
				v-model="username"
				label="Username"
				outlined
				:disabled="state != STATES.DEFAULT"

				:maxlength="100"
				counter
			></v-text-field>

			<v-text-field
				v-model="url"
				label="URL"
				outlined
				:disabled="state != STATES.DEFAULT"

				:maxlength="100"
				counter
			></v-text-field>

			<v-textarea
				v-model="notes"
				label="Notes"
				outlined
				:disabled="state != STATES.DEFAULT"

				:maxlength="1000"
				counter
			></v-textarea>

			<v-progress-linear
				:active="state == STATES.SAVING"
				indeterminate
				color="primary"
				style="margin-bottom: 24px;"
			></v-progress-linear>

			<v-row style="padding-left: 12px; padding-right: 12px; margin-top: 8px; margin-bottom: 8px;">
				<v-spacer></v-spacer>
				<v-btn
					style="margin-right: 8px;"
					:disabled="state != STATES.DEFAULT"
					@click="onBackClick()"
				>Cancel</v-btn>
				<v-btn
					color="primary"
					:disabled="state != STATES.DEFAULT"
					@click="onSubmitClick()"
				>
					Save
				</v-btn>
			</v-row>
		</div>

		<v-container style="flex: 1 1 auto;"
			v-if="state == STATES.LOADING"
		>
			<div style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
				<v-progress-circular
					style="margin: 0 auto; text-align:center;"
					:size="64"
					color="primary"
					indeterminate
				></v-progress-circular>
			</div>
		</v-container>
	</div>
</template>

<script>

const STATES = {
	INITIAL: 0,
	DEFAULT: 1,
	LOADING: 2,
	SAVING: 3
};
const MODES = {
	ADDING: 0,
	EDITING: 1
};

export default {
	name: "BoardPasswordEdit",

	data: () => ({
		state: STATES.INITIAL,
		stateTimeout: null,

		mode: MODES.EDITING,
		title: null,
		titleErrors: [],
		username: null,
		url: null,
		notes: null,

		password: "********",
		passwordErrors: [],
		passwordShow: false,
		passwordUnlocked: false,
		unlockIcon: 'mdi-lock',
		unlockPasswordDialog: false,

		selectedTab: null,
		selectedTabErrors: [],
		tabs: []
	}),

	computed: {
		STATES: () => {
			return STATES;
		},
		MODES: () => {
			return MODES;
		}
	},

	async mounted(){
		await this.loadData();
	},

	methods: {
		async loadData(){
			var that = this;
			if(this.stateTimeout != null){
				clearTimeout(this.stateTimeout);
			}
			this.stateTimeout = setTimeout(function(){
				that.state = STATES.LOADING;
				that.stateTimeout = null;
			});

			let passwordCode = this.$route.params.password_id;

			if(typeof(passwordCode) !== 'undefined'){
				this.mode = MODES.EDITING;

				let password = await this.$store.dispatch("board/getPasswordData", {
					boardId: this.$route.params.board_id,
					passwordCode: passwordCode
				});

				this.title = password.title;
				this.username = password.username;
				this.url = password.url;
				this.notes = password.description;
				this.selectedTab = password.tabId;
				this.passwordUnlocked = false;
				this.password = '********';
				this.passwordShow = false;
			}
			else {
				this.mode = MODES.ADDING;

				await this.$store.dispatch("board/getData", {
					id: this.$route.params.board_id,
					allowCache: true
				});

				this.title = null;
				this.username = null;
				this.url = null;
				this.notes = null;
				this.selectedTab = null;
				this.passwordUnlocked = true;
				this.password = null;
				this.passwordShow = false;
			}

			this.tabs.splice(0, this.tabs.length);
			let tabs = this.$store.getters["board/getTabs"];
			for(let i = 0; i < tabs.length; i++){
				this.tabs.push({
					id: tabs[i].id,
					name: tabs[i].name
				});
			}

			if(this.stateTimeout != null){
				clearTimeout(this.stateTimeout);
			}
			this.stateTimeout = null;
			this.state = STATES.DEFAULT;
		},

		onBackClick(){
			this.$router.push("/board/" + this.$route.params.board_id);
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
				await this.$store.dispatch("board/addPassword", {
					boardId: this.$route.params.board_id,
					boardTabId: this.selectedTab,
					password: this.password,
					title: this.title,
					description: this.notes,
					url: this.url,
					username: this.username
				});

				this.$emit("added");
			}
			else {
				await this.$store.dispatch("board/updatePassword", {
					boardId: this.$route.params.board_id,
					passwordCode: this.$route.params.password_id,
					boardTabId: this.selectedTab,
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
			this.$router.push("/board/" + this.$route.params.board_id);
		}
	}
}
</script>

<style scoped>

</style>