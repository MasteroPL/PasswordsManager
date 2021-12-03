<template>
	<v-dialog
		v-model="model"
		max-width="300px"
		persistent
	>
		<v-card
		>
			<v-card-title>Delete password?</v-card-title>
			<v-divider></v-divider>

			<v-card-text style="padding-top: 20px">
				Are you sure you want to delete the password? This action <b><u>cannot be undone</u></b>!
			</v-card-text>

			<v-divider v-if="!loader"></v-divider>
			<v-progress-linear 
				v-else
				indeterminate 
				color="primary"
			></v-progress-linear>

			<v-card-actions>
				<v-spacer></v-spacer>

				<v-btn
					text
					:disabled="loader"
					@click="model = false;"
				>Cancel</v-btn>
				<v-btn
					color="red"
					text
					:disabled="loader"
				>Delete</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script>

export default {
	name: "GenericDeletePasswordDialog",
	props: {
		passwordId: {
			type: String,
			required: false,
			default: null
		}
	},

	data: () => ({
		model: false,
		loader: false
	}),

	methods: {
		open(){
			this.loader = false;
			this.model = true;
		},
		close() {
			this.model = false;
		}
	}
}
</script>

<style scoped>

</style>