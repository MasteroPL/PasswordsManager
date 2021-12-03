<template>
	<div>
		<v-dialog
			scrollable
			max-width="350px"
			v-model="model"
		>
			<v-card style="position: relative">
				<v-card-title>Password details</v-card-title>

				<div class="board-details-dialog__actions">
					<v-tooltip bottom v-if="permissionUpdate">
						<template v-slot:activator="{ on, attrs }">
							<v-btn
								icon
								color="secondary"
								v-on="on"
								v-bind="attrs"
								@click="onEditClick()"
							>
								<v-icon>mdi-pencil</v-icon>
							</v-btn>
						</template>

						<span>Update password or password details</span>
					</v-tooltip>

					<v-tooltip bottom>
						<template v-slot:activator="{ on, attrs }">
							<v-btn
								v-if="permissionDelete"
								icon
								color="red"
								v-on="on"
								v-bind="attrs"
								@click="onDeleteClick()"
							>
								<v-icon>mdi-delete</v-icon>
							</v-btn>
						</template>

						<span>Delete password</span>
					</v-tooltip>
				</div>

				<v-divider></v-divider>

				<v-list
				>
					<!-- Title -->
					<v-list-item>
						<v-list-item-content>
							<v-list-item-subtitle>TITLE</v-list-item-subtitle>
							<v-list-item-title>{{ title }}</v-list-item-title>
						</v-list-item-content>
					</v-list-item>

					<!-- Username -->
					<v-list-item
						@click="onPasswordDialogUsernameCopyClick()"
						v-if="username != null"
					>
						<v-list-item-content>
							<v-list-item-subtitle>USERNAME</v-list-item-subtitle>
							<v-list-item-title>{{ username }}</v-list-item-title>
						</v-list-item-content>

						<v-list-item-action>
							<v-icon color="secondary"
								v-if="usernameCopyTimeout == null"
							>mdi-content-copy</v-icon>
							<v-icon color="secondary"
								v-else
							>mdi-check</v-icon>
						</v-list-item-action>
					</v-list-item>

					<!-- Password -->
					<v-list-item
						:disabled="!permissionRead || passwordCopyLoader"
						@click="onPasswordDialogPasswordCopyClick()"
					>
						<v-list-item-content>
							<v-list-item-subtitle>PASSWORD</v-list-item-subtitle>
							<v-list-item-title>********</v-list-item-title>
						</v-list-item-content>

						<v-list-item-action v-if="permissionRead">
							<v-progress-circular
								indeterminate
								:size="24"
								v-if="passwordCopyLoader"
							></v-progress-circular>
							<v-icon color="secondary"
								v-else-if="passwordCopyTimeout == null"
							>mdi-content-copy</v-icon>
							<v-icon color="secondary"
								v-else
							>mdi-check</v-icon>
						</v-list-item-action>
					</v-list-item>

					<!-- URL -->
					<v-list-item
						@click="onPasswordDialogUrlCopyClick()"
						v-if="url != null"
					>
						<v-list-item-content>
							<v-list-item-subtitle>URL</v-list-item-subtitle>
							<v-list-item-title>{{ url }}</v-list-item-title>
						</v-list-item-content>

						<v-list-item-action>
							<v-icon color="secondary"
								v-if="urlCopyTimeout == null"
							>mdi-content-copy</v-icon>
							<v-icon color="secondary"
								v-else
							>mdi-check</v-icon>
						</v-list-item-action>
					</v-list-item>

					<!-- Notes -->
					<v-list-item
						v-if="notes != null"
					>
						<v-list-item-content>
							<v-list-item-subtitle>NOTES</v-list-item-subtitle>
							<v-list-item-title class="board-details-dialog__notes" v-html="$data._notes"></v-list-item-title>
						</v-list-item-content>
					</v-list-item>
				</v-list>

				<v-divider></v-divider>

				<v-card-actions>
					<v-spacer></v-spacer>
					<v-btn
						text
						@click="model = false;"
					>
						Close
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<GenericDeletePasswordDialog
			ref="GenericDeletePasswordDialog"
			:passwordId="passwordId"
		></GenericDeletePasswordDialog>
	</div>
</template>

<script>
import GenericDeletePasswordDialog from '@/generic/GenericDeletePasswordDialog.vue'

const SURROGATE_PAIR_REGEXP = /[\uD800-\uDBFF][\uDC00-\uDFFF]/g,
    // Match everything outside of normal chars and " (quote character)
    NON_ALPHANUMERIC_REGEXP = /([^#-~| |!])/g;

export default {
	name: "GenericPasswordDetailsDialog",

	components: {
		"GenericDeletePasswordDialog": GenericDeletePasswordDialog
	},
	
	props: {
		passwordId: {
			type: String,
			required: false,
			default: null
		},
		title: {
			type: String,
			required: true
		},
		username: {
			type: String,
			required: false,
			default: null
		},
		url: {
			type: String,
			required: false,
			default: null
		},
		notes: {
			type: String,
			required: false,
			default: null
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
		},
		permissionRead: {
			type: Boolean,
			required: false,
			default: false
		}
	},
	
	data: () => ({
		_notes: null,
		model: false,
		requestId: 0, // allows to ignore cancelled requests

		usernameCopyTimeout: null,
		urlCopyTimeout: null,
		passwordCopyLoader: false,
		passwordCopyTimeout: null
	}),

	methods: {
		
		open(){
			if(this.usernameCopyTimeout != null){
				clearTimeout(this.usernameCopyTimeout);
				this.usernameCopyTimeout = null;
			}
			if(this.passwordCopyTimeout != null){
				clearTimeout(this.passwordCopyTimeout);
				this.passwordCopyTimeout = null;
			}
			if(this.urlCopyTimeout != null){
				this.urlCopyTimeout = null;
			}
			this.passwordCopyLoader = false;

			if(this.notes != null){
				var tmpNotes = this.notes;
				tmpNotes = this.encodeEntities(tmpNotes);
				tmpNotes = tmpNotes.replace(/&#10;/g, "<br />");
				this.$data._notes = tmpNotes;
			}

			this.model = true;
		},
		close(){
			this.model = false;
		},



		/**
		* Escapes all potentially dangerous characters, so that the
		* resulting string can be safely inserted into attribute or
		* element text.
		* @param value
		* @returns {string} escaped text
		*/
		encodeEntities(value) {
			console.log(value);
			return value.
				replace(/&/g, '&amp;').
				replace(SURROGATE_PAIR_REGEXP, function(value) {
					var hi = value.charCodeAt(0);
					var low = value.charCodeAt(1);
					return '&#' + (((hi - 0xD800) * 0x400) + (low - 0xDC00) + 0x10000) + ';';
				}).
				replace(NON_ALPHANUMERIC_REGEXP, function(value) {
					return '&#' + value.charCodeAt(0) + ';';
				}).
				replace(/</g, '&lt;').
				replace(/>/g, '&gt;');
		},

		//
		// Event Handlers
		//
		onPasswordDialogUsernameCopyClick(){
			if (this.usernameCopyTimeout != null){
				clearTimeout(this.usernameCopyTimeout);
			}

			navigator.clipboard.writeText(this.username);
			var that = this;
			this.usernameCopyTimeout = setTimeout(function(){
				that.usernameCopyTimeout = null;
			}, 750);
		},

		onPasswordDialogPasswordCopyClick(){
			if(this.passwordCopyLoader){
				return;
			}

			if (this.passwordCopyTimeout != null){
				clearTimeout(this.passwordCopyTimeout);
				this.passwordCopyTimeout = null;
			}

			var requestId = (++this.requestId);

			this.passwordCopyLoader = true;
			// TODO: download password
			// For now timeout to simulate
			var that = this;
			setTimeout(function(){
				if(requestId == that.requestId){
					that.passwordCopyLoader = false;
					
					navigator.clipboard.writeText("PASSWORD123!");
					that.passwordCopyTimeout = setTimeout(function(){
						that.passwordCopyTimeout = null;
					}, 750);
				}
			}, 2000);			
		},

		onPasswordDialogUrlCopyClick(){
			if (this.urlCopyTimeout != null){
				clearTimeout(this.urlCopyTimeout);
			}

			navigator.clipboard.writeText(this.url);
			var that = this;
			this.urlCopyTimeout = setTimeout(function(){
				that.urlCopyTimeout = null;
			}, 750);
		},

		onEditClick(){
			this.$router.push("/board/" + this.$route.params.board_id + "/password/" + this.passwordId);
		},

		onDeleteClick(){
			this.$refs.GenericDeletePasswordDialog.open();
		}
	}
}

</script>

<style scoped>
	.board-details-dialog__notes {
		white-space: normal;
		text-overflow: unset;
	}

	.board-details-dialog__actions {
		position: absolute;
		right: 8px;
		top: 12px;
	}
</style>