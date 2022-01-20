<template>
	<div class="user-password-shares-container" style="padding-top: 12px; height: 100%; display: flex; flex-direction: column; padding-left: 8px; padding-right: 8px; max-width: 600px;">
		<div>
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
			<h2>Password Shares</h2>
			<div class="user-password-shares__header-subtitle">
				{{ passwordTitle }}
			</div>

			<v-divider></v-divider>

			<v-row style="margin-top: 12px; margin-right: 0">
				<v-spacer></v-spacer>
				<v-btn
					color="primary"
					@click="onAddShareClick()"
				>
					Add share
					<v-icon
						right
						dark
					>mdi-plus</v-icon>
				</v-btn>
			</v-row>

			<div
				v-if="shares.length == 0"
				class="user-password-shares__list-empty-header"
				style="opacity: 0.8; margin-top: 32px; text-align: center"
			>
				<h4>List is empty</h4>
			</div>
			<v-list
				v-else
				class="user-password-shares__list"
			>
				<v-list-item
					v-for="item in shares"
					:key="item.shareId"
				>
					<v-list-item-content two-line>
						<v-list-item-title>{{ item.username }}</v-list-item-title>
						<v-list-item-subtitle>{{ item.fullName }}</v-list-item-subtitle>
					</v-list-item-content>

					<v-list-item-action>
						<v-btn
							icon
							text
							@click="onDeleteClick(item)"
						>
							<v-icon color="red">mdi-delete</v-icon>
						</v-btn>
					</v-list-item-action>
				</v-list-item>
			</v-list>
		</div>

		<GenericAddShareDialog
			ref="GenericAddShareDialog"
			:passwordCode="passwordCode"

			@shareAdded="onShareAdded()"
		></GenericAddShareDialog>

		<GenericDeleteShareDialog
			ref="GenericDeleteShareDialog"
			:passwordCode="passwordCode"
			:shareId="deleteShareDialog.shareId"
			:user="deleteShareDialog.user"

			@deleted="onShareDeleted()"
		></GenericDeleteShareDialog>
	</div>
</template>

<script>
//import ERRORS from '@/consts/standardErrors'
import GenericAddShareDialog from '@/generic/GenericAddShareDialog.vue'
import GenericDeleteShareDialog from '@/generic/GenericDeleteShareDialog.vue'

const STATES = {
	INITIAL: 0,
	DEFAULT: 1,
	SAVING: 3,
};

export default {
	name: "UserPasswordShare",

	components: {
		"GenericAddShareDialog": GenericAddShareDialog,
		"GenericDeleteShareDialog": GenericDeleteShareDialog
	},

	data: () => ({
		state: STATES.INITIAL,

		passwordTitle: "Sample title",

		shares: [], // [
		// 	{
		// 		shareId: {Number},
		// 		userId: {Number},
		// 		username: {String},
		// 		subtitle1: {String},
		// 	}
		// ]

		deleteShareDialog: {
			shareId: -1,
			user: ""
		}
	}),
	computed: {
		STATES: () => {
			return STATES;
		},
		passwordCode() {
			return this.$route.params.password_id;
		}
	},

	async mounted() {
		await this.loadData();
		this.state = STATES.DEFAULT;
	},

	methods: {
		async loadData(){
			let password = null;

			for(let i = 0; i < 2; i++){
				password = this.$store.getters["userPasswords/getPassword"](this.$route.params.password_id);

				if(password == null){
					await this.$store.dispatch("userPasswords/getData", {
						allowCache: false
					});
				}
			}

			if (password == null){
				this.$router.push("/user-passwords/");
			}

			this.passwordTitle = password.title;
			this.shares = password.shares;
		},

		onBackClick(){
			this.$router.push("/user-passwords/");
		},

		onAddShareClick(){
			this.$refs.GenericAddShareDialog.open();
		},

		onShareAdded(){
			this.loadData();
		},

		onShareDeleted(){
			this.loadData();
		},

		onDeleteClick(item){
			this.deleteShareDialog.shareId = item.shareId;
			this.deleteShareDialog.user = item.username + " (" + item.fullName + ")";
			this.$refs.GenericDeleteShareDialog.open();
		}
	}
}

</script>

<style scoped>
.user-password-shares__header-subtitle{
	padding-bottom: 8px;
}

.user-password-shares__list {
	background: none;
	background-color: none;
	margin-top: 16px;
}
</style>