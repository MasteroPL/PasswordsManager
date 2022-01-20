<template>
	<v-dialog
		v-model="model"
		max-width="320"
	>
		<v-card>
			<v-card-title>Delete share?</v-card-title>
			<v-divider></v-divider>

			<v-card-text style="padding-top: 20px">
				Are you sure you want to delete the share for user <b>{{ user }}</b>?
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
					@click="onSubmit()"
				>Delete</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script>

export default {
	name: "GenericDeleteShareDialog",

	props: {
		shareId: {
			type: Number,
			required: true
		},
		user: {
			type: String,
			required: true
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

		close(){
			this.model = false;
		},

		async onSubmit(){
			await this.$store.dispatch("userPasswords/deleteShare", {
				passwordCode: this.$route.params.password_id,
				shareId: this.shareId
			});

			this.$emit("deleted");
			this.close();
		}	
	}
}

</script>