<template>
	<v-dialog
		v-model="model"
		max-width="300"
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

			<v-card-actions>
				<v-spacer></v-spacer>

				<v-btn
					text
					@click="close()"
				>Cancel</v-btn>
				<v-btn
					text
					color="red"
				>Remove</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script>
export default {
	name: "GenericRemoveBoardUserDialog",

	props: {
		userId: {
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
		model: false
	}),
	mounted() {

	},
	methods: {
		open(){
			this.model = true;
		},
		close() {
			this.model = false;
		}
	}
}
</script>