<template>
	<v-dialog
		v-model="model"
		max-width="300"
		:persistent="controlsDisabled"
	>
		<v-card>
			<v-card-title>Remove board user</v-card-title>

			<v-divider style="margin-bottom: 20px;"></v-divider>

			<v-card-text v-if="userDisplayName != null">
				Are you sure you want to remove <b>{{ userDisplayName }}</b> from the board?
			</v-card-text>
			<v-card-text v-else>
				Are you sure you want to remove user from the board?
			</v-card-text>

			<v-divider></v-divider>

			<v-progress-linear
				:active="loading"
				indeterminate
				color="primary"
			></v-progress-linear>

			<v-card-actions>
				<v-spacer></v-spacer>

				<v-btn
					text
					:disabled="controlsDisabled"
					@click="close()"
				>Cancel</v-btn>
				<v-btn
					text
					:disabled="controlsDisabled"
					color="red"
					@click="onSubmit()"
				>Remove</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script>
export default {
	name: "GenericRemoveBoardUserDialog",

	props: {
		assignmentId: {
			type: Number,
			required: true
		},
		boardId: {
			type: Number,
			required: true
		},
		// Will appear in confirmation dialog if provided
		userDisplayName: {
			type: String,
			required: false,
			default: null
		}
	},

	data: () => ({
		model: false,

		loading: false,
		loaderTimeout: null,
		controlsDisabled: false
	}),
	mounted() {

	},
	methods: {
		open(){
			this.model = true;
		},
		close() {
			this.model = false;
		},

		async onSubmit(){
			var that = this;
			this.controlsDisabled = true;
			if(this.loaderTimeout != null){
				clearTimeout(this.loaderTimeout);
			}
			this.loaderTimeout = setTimeout(function(){
				that.loaderTimeout = null;
				that.loading = true;
			});

			let exception = false;
			try {
				await this.$store.dispatch("board/removeUserAssignment", {
					boardId: this.boardId,
					assignmentId: this.assignmentId
				});
			} catch(error){
				exception = true;
				console.log(error);

				// TODO
			} finally {
				if(this.loaderTimeout != null){
					clearTimeout(this.loaderTimeout);
				}
				this.loaderTimeout = null;
				this.loading = false;
				this.controlsDisabled = false;
			}

			if(exception){
				return;
			}

			this.$emit("deleted");

			this.close();
		}
	}
}
</script>