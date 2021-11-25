<template>
	<div
		class="BoardAdd"
	>
		<h2 style="padding-left: 4px; margin-bottom: 8px;">New board</h2>

		<v-divider style="margin-bottom: 16px;"></v-divider>

		<v-text-field
			v-model="boardName"
			style="max-width: 400px"
			outlined
			label="Board name"
			required
			counter
			:maxlength="50"
			:error-messages="boardNameError != null ? [ boardNameError ] : []"
			@input="boardNameError=null"

			:disabled="disableControls"
		></v-text-field>

		<v-textarea
			v-model="boardDescription"
			label="Board description"
			outlined
			style="max-width: 600px;"
			required
			counter
			:maxlength="1024"
			:error-messages="boardDescriptionError != null ? [ boardDescriptionError ] : []"
			@input="boardDescriptionError=null"

			:disabled="disableControls"
		></v-textarea>

		<v-progress-linear
			style='margin-bottom: 8px;'
			:active="state == STATES.LOADING"
			indeterminate
			color="primary"
		></v-progress-linear>

		<v-row
			style="margin-left: 0; margin-right: 0; margin-top: 0px;"
		>
			<v-spacer></v-spacer>
			<v-btn
				style="margin-right: 8px;"
				@click="onCancelClick()"

				:disabled="disableControls"
			>Cancel</v-btn>

			<v-btn
				color="primary"
				@click="onSubmitClick()"

				:disabled="disableControls"
			>Add</v-btn>
		</v-row>

		<!-- Error dialog -->
		<v-dialog
			v-model="errorDialog.model"
			max-width="290"
		>
			<v-card>
				<v-card-title>
					{{ errorDialog.title }}
				</v-card-title>

				<v-divider></v-divider>

				<v-card-text style="padding-top: 20px">
					{{ errorDialog.description }}
				</v-card-text>

				<v-divider></v-divider>

				<v-card-actions>
					<v-spacer></v-spacer>

					<v-btn
						text
						@click="errorDialog.model=false"
					>OK</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</div>
</template>

<script>
const STATES = {
	DEFAULT: 0,
	LOADING: 1
};

import ERRORS from '@/consts/standardErrors'

export default {
	name: "BoardAdd",
	data: () => ({
		state: STATES.DEFAULT,
		disableControls: false,
		boardName: "",
		boardNameError: null,
		boardDescription: "",
		boardDescriptionError: null,

		submitTimeout: null,

		errorDialog: {
			model: false,
			title: "An error occured",
			description: "An unknown error occured, please try again later"
		}
	}),
	computed: {
		STATES: () => {
			return STATES;
		}
	},
	mounted() {

	},
	methods: {
		onCancelClick(){
			this.$router.push("/boards/");
		},
		async onSubmitClick(){
			this.disableControls = true;
			var that = this;
			if(this.submitTimeout != null){
				clearTimeout(this.submitTimeout);
			}
			this.submitTimeout = setTimeout(function(){
				that.state = STATES.LOADING;
				that.submitTimeout = null;
			}, 200);

			let data = {
				name: this.boardName,
				description: this.boardDescription
			};

			let exception = false;
			try {
				await this.$store.dispatch("boardsList/addBoard", data);
			} catch (error){
				exception = true;
				switch (error.type){
					case ERRORS.VALIDATION:
						if(typeof(error.errors.name) !== 'undefined'){
							this.boardNameError = error.errors.name.string;
						}
						if(typeof(error.errors.description) !== 'undefined'){
							this.boardDescriptionError = error.errors.description.string;
						}
						break;

					case ERRORS.UNATHORIZED:
						this.$router.push("/login/");
						break;

					case ERRORS.FORBIDDEN:
						this.$router.push("/login/");
						break;

					case ERRORS.NETWORK_ERROR:
						this.errorDialog.title = "Network error";
						this.errorDialog.description = "Could not establish connection with the server. Please check if you are connected to the internet";
						this.errorDialog.model = true;
						break;
					
					default:
						this.errorDialog.title = "Unknown error";
						this.errorDialog.description = "An unknown error has occured. That is all we know.";
						this.errorDialog.model = true;
				}
			} finally {
				if(this.submitTimeout != null){
					clearTimeout(this.submitTimeout);
					this.submitTimeout = null;
				}

				this.disableControls = false;
				this.state = STATES.DEFAULT;
			}

			if(exception){
				return;
			}

			this.$router.push("/boards/");
		}
	}
}
</script>

<style scoped>
.BoardAdd {
	max-width: 600px;
	padding: 16px;
	margin-top: 8px;
}
</style>