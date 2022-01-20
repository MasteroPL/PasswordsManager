<template>
	<div class="change-password-container" style="height: 100%; padding-top: 18px; display: flex; flex-direction: column;">
		<h2 style="padding-bottom: 16px; ">Change Password</h2>

		<v-divider></v-divider>

		<div style='padding-top: 24px'>
			<v-text-field
				v-model="oldPassword"
				label="Old password"
				outlined
				:type="showPassword1 ? 'text' : 'password'"
				:append-icon="showPassword1 ? 'mdi-eye' : 'mdi-eye-off'"
				@click:append="showPassword1 = !showPassword1"
				:maxlength="128"
				:error-messages="oldPasswordErrors"
				@keyup.enter.native="onSubmitClick()"
			></v-text-field>

			<v-text-field
				v-model="newPassword"
				label="New password"
				outlined
				:type="showPassword2 ? 'text' : 'password'"
				:append-icon="showPassword2 ? 'mdi-eye' : 'mdi-eye-off'"
				@click:append="showPassword2 = !showPassword2"
				:maxlength="128"
				:error-messages="newPasswordErrors"
				@keyup.enter.native="onSubmitClick()"
			></v-text-field>

			<v-text-field
				v-model="repeatNewPassword"
				label="Repeat new password"
				outlined
				:type="showPassword3 ? 'text' : 'password'"
				:append-icon="showPassword3 ? 'mdi-eye' : 'mdi-eye-off'"
				@click:append="showPassword3 = !showPassword3"
				:maxlength="128"
				:error-messages="repeatNewPasswordErrors"
				@keyup.enter.native="onSubmitClick()"
			></v-text-field>

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
					Submit
				</v-btn>
			</v-row>
		</div>
	</div>
</template>

<script>
import ERRORS from '@/consts/standardErrors'

const STATES = {
	DEFAULT: 0,
	SAVING: 1
};

export default {
	name: "ChangePassword",

	data: () => ({
		state: STATES.DEFAULT,

		showPassword1: false,
		showPassword2: false,
		showPassword3: false,

		oldPassword: null,
		oldPasswordErrors: [],

		newPassword: null,
		newPasswordErrors: [],

		repeatNewPassword: null,
		repeatNewPasswordErrors: []
	}),

	computed: {
		STATES: function(){
			return STATES;
		}
	},

	methods: {
		async onSubmitClick(){
			this.oldPasswordErrors.splice(0, this.oldPasswordErrors.length);
			this.newPasswordErrors.splice(0, this.newPasswordErrors.length);
			this.repeatNewPasswordErrors.splice(0, this.repeatNewPasswordErrors.length);

			let anyErr = false;
			if(this.oldPassword == null || this.oldPassword == ""){
				this.oldPasswordErrors.push("This field is required");
				anyErr = true;
			}

			if(this.newPassword == null || this.newPassword == ""){
				this.newPasswordErrors.push("This field is required");
				anyErr = true;
			}

			if(this.repeatNewPassword == null || this.repeatNewPassword == ""){
				this.repeatNewPasswordErrors.push("This field is required");
				anyErr = true;
			}

			if(anyErr){
				return;
			}

			if(this.newPassword != this.repeatNewPassword){
				this.newPasswordErrors.push("Passwords do not match");
				this.repeatNewPasswordErrors.push("Passwords do not match");
				return;
			}

			this.state = STATES.SAVING;

			try{
				await this.$store.dispatch("changePassword", {
					oldPassword: this.oldPassword,
					newPassword: this.newPassword
				});
			} catch(error){
				this.state = STATES.DEFAULT;
				if (error.type == ERRORS.UNAUTHORIZED){
					this.$emit("logout");
					return;
				}
				else if(error.type == ERRORS.FORBIDDEN){
					this.oldPasswordErrors.push("Password invalid");
					return;
				}
				throw error;
			}
			this.state = STATES.DEFAULT;

			this.$router.push("/my-profile/");
		},

		onBackClick(){
			this.$router.push("/my-profile/");
		}
	}
}
</script>

<style scoped>
.change-password-container {
	max-width: 600px;
	padding-left: 16px;
	padding-right: 16px;
}
</style>