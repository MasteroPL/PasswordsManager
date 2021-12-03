<template>
	<v-dialog
		v-model="model"
		max-width="300"
		persistent
	>
		<v-card>
			<v-card-title v-if="assignmentId != null">Edit access</v-card-title>
			<v-card-title v-else>Add access</v-card-title>

			<!-- User selection if add mode -->
			<template v-if="assignmentId == null">
				<v-divider style="margin-bottom: 20px"></v-divider>
				<v-card-text>
					<v-autocomplete
						:disabled="controlsDisabled"
						v-model="userAutocomplete.model"
						:items="userAutocomplete.items"
						label="User"
						:loading="userAutocomplete.loading"
						item-text="searchValue"
						item-value="id"
						color="secondary"
						placeholder="Start typing to search"
						:search-input.sync="userAutocomplete.searchInput"
						:error-messages="userAutocomplete.errors"
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
					:disabled="controlsDisabled"
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
						:disabled="controlsDisabled"
					></v-checkbox>

					<v-checkbox
						v-model="$data._permissionRead"
						label="Read"
						hide-details
						color="secondary"
						:disabled="controlsDisabled"
					></v-checkbox>

					<v-checkbox
						v-model="$data._permissionUpdate"
						label="Update"
						hide-details
						color="secondary"
						:disabled="controlsDisabled"
					></v-checkbox>

					<v-checkbox
						v-model="$data._permissionDelete"
						label="Delete"
						hide-details
						color="secondary"
						:disabled="controlsDisabled"
					></v-checkbox>
				</v-card-text>
			</div>
			

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
					color="secondary"
					@click="onSubmit()"
				>Save</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script>
import ERRORS from '@/consts/standardErrors.js'
const AUTOCOMPLETER_CONTROLLER = new AbortController();

export default {
	name: "GenericEditBoardUserDialog",

	props: {
		// If user ID not given, dialog will switch to "ADD" mode
		assignmentId: {
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

		loading: false,
		loaderTimeout: null,
		controlsDisabled: false,

		userAutocomplete: {
			model: null,
			loading: false,
			items: [],

			requestId: 0, // Makes sure cancelled requests do not override latest requests
			requestFinished: true,
			loaderTimeout: null,

			searchInput: null,
			searchTimeout: null,
			preventUpdate: false,

			errors: []
		}
	}),
	watch: {
		"userAutocomplete.searchInput": function(){
			if(!this.userAutocomplete.preventUpdate){
				if(this.userAutocomplete.searchTimeout != null){
					clearTimeout(this.userAutocomplete.searchTimeout);
				}
				var that = this;

				this.userAutocomplete.searchTimeout = setTimeout(function(){
					console.log(that.userAutocomplete.searchInput);
					that.onAutocompleteInput(that.userAutocomplete.searchInput);
					that.userAutocomplete.searchTimeout = null;
				}, 500);
			}
			else{
				this.userAutocomplete.preventUpdate = false;
			}
		},
		"userAutocomplete.model": function(){
			this.userAutocomplete.preventUpdate = true;
			this.userAutocomplete.errors.splice(0, this.userAutocomplete.errors.length);
		}
	},
	beforeMount() {

	},
	mounted() {

	},
	methods: {
		open(){
			var that = this;
			this.userAutocomplete.model = null;
			this.userAutocomplete.items.splice(0, this.userAutocomplete.items.length);

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
		},

		async onAutocompleteInput(inputValue){
			this.userAutocomplete.errors.splice(0, this.userAutocomplete.errors.length);
			if(!this.userAutocomplete.requestFinished){
				AUTOCOMPLETER_CONTROLLER.abort();
			}

			if(this.userAutocomplete.loaderTimeout != null){
				clearTimeout(this.userAutocomplete.loaderTimeout);
			}

			this.userAutocomplete.requestFinished = false;
			var requestId = ++this.userAutocomplete.requestId;

			var that = this;
			this.userAutocomplete.loaderTimeout = setTimeout(function(){
				that.userAutocomplete.loaderTimeout = null;
				that.userAutocomplete.loading = true;
			}, 200);

			let response = null;
			let exception = false;
			try {
				response = await this.$store.dispatch("board/searchAddUser", {
					boardId: this.boardId,
					searchValue: inputValue,
					abortControllerSignal: AUTOCOMPLETER_CONTROLLER.signal
				});
			} catch(error) {
				exception = true;
			
				switch(error.type){
					case ERRORS.VALIDATION:
						if(typeof(error.errors.searchValue) !== 'undefined'){
							this.userAutocomplete.errors.splice(0, this.userAutocomplete.errors.length);
							this.userAutocomplete.errors.push(error.errors.searchValue.string);
						}
				}
			} finally {
				if(requestId == this.userAutocomplete.requestId){
					this.userAutocomplete.requestFinished = true;
					if(this.userAutocomplete.loaderTimeout != null){
						clearTimeout(this.userAutocomplete.loaderTimeout);
						this.userAutocomplete.loaderTimeout = null;
					}
					this.userAutocomplete.loading = false;
				}
			}

			if(exception){
				return;
			}

			this.userAutocomplete.items = response;
		},

		validateSubmitCreate(){
			this.userAutocomplete.errors.splice(0, this.userAutocomplete.errors.length);

			if (this.userAutocomplete.model == null || this.userAutocomplete.model == ""){
				this.userAutocomplete.errors.push("This field is required");
				return false;
			}

			return true;
		},

		async submitCreate(){
			if(this.validateSubmitCreate()){
				let payload = {
					boardId: this.boardId,
					userId: this.userAutocomplete.model
				};

				if(this.canAddAdministrators){
					payload.admin = this.$data._administrator;
				}

				payload.create = this.$data._permissionCreate;
				payload.read = this.$data._permissionRead;
				payload.update = this.$data._permissionUpdate;
				payload.delete = this.$data._permissionDelete;

				let response = null;
				try {
					response = await this.$store.dispatch("board/assignUser", payload);
				} catch(error){
					console.log(error);

					// TODO

					return;
				}

				this.$emit("created", response);
				this.close();
			}
		},

		async submitEdit() {
			let payload = {
				boardId: this.boardId,
				assignmentId: this.assignmentId
			};

			if(this.canAddAdministrators){
				payload.admin = this.$data._administrator;
			}

			payload.create = this.$data._permissionCreate;
			payload.read = this.$data._permissionRead;
			payload.update = this.$data._permissionUpdate;
			payload.delete = this.$data._permissionDelete;

			let response = null;
			try {
				response = await this.$store.dispatch("board/editUserAssignment", payload);
			} catch(error){
				console.log(error);

				// TODO

				return;
			}

			this.$emit("updated", response);
			this.close();
		},

		async onSubmit(){
			var that = this;
			this.controlsDisabled = true;
			if(this.loaderTimeout != null){
				clearTimeout(this.loaderTimeout);
			}
			this.loaderTimeout = setTimeout(function(){
				that.loading = true;
				that.loaderTimeout = null;
			});

			if(this.assignmentId == null){
				await this.submitCreate();
			}
			else{
				await this.submitEdit();
			}

			if(this.loaderTimeout != null){
				clearTimeout(this.loaderTimeout);
				this.loaderTimeout = null;
			}
			this.controlsDisabled = false;
			this.loading = false;
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