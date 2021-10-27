<template>
	<v-dialog
		v-model="model"
		max-width="300"
		persistent
	>
		<v-card>
			<v-card-title v-if="userId != null">Edit access</v-card-title>
			<v-card-title v-else>Add access</v-card-title>

			<!-- User selection if add mode -->
			<template v-if="userId == null">
				<v-divider style="margin-bottom: 20px"></v-divider>
				<v-card-text>
					<v-autocomplete
						v-model="userAutocomplete.model"
						:items="userAutocomplete.items"
						label="User"
						item-text="name"
						item-value="id"
						color="secondary"
					></v-autocomplete>
				</v-card-text>
			</template>

			<v-divider :style="(canAddAdministrators) ? 'margin-bottom: 16px' : ''"></v-divider>

			<v-card-text style="padding-bottom: 0">
				<v-checkbox
					v-model="$data._administrator"
					hide-details
					color="secondary"
					v-if="canAddAdministrators"
				>
					<template v-slot:label>
						<span style="color:red">Administrator</span>
					</template>
				</v-checkbox>
			</v-card-text>

			<div
				class="generic-edit-board-user-dialog__expansion-panel"
				:style="($data._administrator) ? 'height: 0' : (canAddAdministrators) ? 'height: 193px;' : 'height: 193px; margin-top: 0'"
			>
				<v-card-text style="padding-left: 24px; padding-right: 24px; padding-top:0">
					<v-divider v-if="canAddAdministrators"></v-divider>

					<v-checkbox
						v-model="$data._permissionCreate"
						label="Create"
						hide-details
						color="secondary"
					></v-checkbox>

					<v-checkbox
						v-model="$data._permissionRead"
						label="Read"
						hide-details
						color="secondary"
					></v-checkbox>

					<v-checkbox
						v-model="$data._permissionUpdate"
						label="Update"
						hide-details
						color="secondary"
					></v-checkbox>

					<v-checkbox
						v-model="$data._permissionDelete"
						label="Delete"
						hide-details
						color="secondary"
					></v-checkbox>
				</v-card-text>
			</div>
			

			<v-divider></v-divider>

			<v-card-actions>
				<v-spacer></v-spacer>

				<v-btn
					text
					@click="close()"
				>Cancel</v-btn>
				<v-btn
					text
					color="secondary"
				>Save</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script>

export default {
	name: "GenericEditBoardUserDialog",

	props: {
		// If user ID not given, dialog will switch to "ADD" mode
		userId: {
			type: Number,
			required: false,
			default: null
		},
		boardId: {
			type: Number,
			required: true
		},
		canAddAdministrators: {
			type: Boolean,
			required: false,
			default: false
		},
		administrator: {
			type: Boolean,
			required: false,
			default: false
		},
		permissionCreate: {
			type: Boolean,
			required: false,
			default: false
		},
		permissionRead: {
			type: Boolean,
			required: false,
			default: false
		},
		permissionUpdate: {
			type: Boolean,
			required: false,
			default: false
		},
		permissionDelete: {
			type: Boolean,
			required: false,
			default: false
		}
	},

	data: () => ({
		model: false,
		_administrator: false,
		_permissionCreate: false,
		_permissionRead: false,
		_permissionUpdate: false,
		_permissionDelete: false,

		userAutocomplete: {
			model: null,
			items: []
		}
	}),

	beforeMount() {

	},
	mounted() {

	},
	methods: {
		open(){
			var that = this;

			this.$nextTick(function(){
				this.$data._administrator = this.administrator;
				this.$data._permissionCreate = this.permissionCreate;
				this.$data._permissionRead = this.permissionRead;
				this.$data._permissionUpdate = this.permissionUpdate;
				this.$data._permissionDelete = this.permissionDelete;

				if(!this.canAddAdministrators){
					this.$data._administrator = false;
				}

				
				this.$nextTick(function(){
					that.model = true;
				});
			});
		},

		close() {
			this.model = false;
		}
	}
}
</script>

<style scoped>
	.generic-edit-board-user-dialog__expansion-panel{
		overflow-y: hidden;
		transition: height 0.2s ease-in-out;
		margin-top: 16px;
	}
</style>