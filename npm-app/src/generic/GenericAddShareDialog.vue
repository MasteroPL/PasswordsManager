<template>
	<div class="generic-add-share-dialog-container">
		<v-dialog
			v-model="model"
			max-width="350"
		>
			<v-card>
				<v-card-title>
					Add share
				</v-card-title>

				<v-divider></v-divider>

				<v-card-text style="padding-top: 20px">
					<v-autocomplete
						v-model="userAutocomplete.model"
						:items="userAutocomplete.items"
						label="User"
						:loading="userAutocomplete.loading"
						item-text="searchValue"
						item-value="id"
						placeholder="Start typing to search"
						:search-input.sync="userAutocomplete.searchInput"
						:error-messages="userAutocomplete.errors"
					></v-autocomplete>
				</v-card-text>

				<v-divider v-if="state == STATES.DEFAULT"></v-divider>
				<v-progress-linear
					:active="state == STATES.SAVING"
					indeterminate
					color="primary"
					style="margin-bottom: 24px;"
				></v-progress-linear>

				<v-card-actions>
					<v-spacer></v-spacer>

					<v-btn
						text
						:disabled="state == STATES.SAVING"
						@click="close()"
					>Cancel</v-btn>
					<v-btn
						text
						:disabled="state == STATES.SAVING"
						color="primary"
						@click="onSubmit()"
					>Share</v-btn>
				</v-card-actions>

			</v-card>
		</v-dialog>
	</div>
</template>

<script>
import ERRORS from '@/consts/standardErrors.js'
const AUTOCOMPLETER_CONTROLLER = new AbortController();
const STATES = {
	DEFAULT: 0,
	SAVING: 1
};

export default {
	name: "GenericAddShareDialog",

	props: {
		passwordCode: {
			type: String,
			required: true
		}
	},

	data: () => ({
		state: STATES.DEFAULT,
		model: false,
		userAutocomplete: {
			model: null,
			items: [],
			searchInput: "",
			errors: [],

			requestId: 0,
			requestFinished: true,
			loaderTimeout: null,
			loading: false,

			preventUpdate: false,
			searchTimeout: null
		}
	}),

	computed: {
		STATES: () => {
			return STATES;
		}
	},

	watch: {
		"userAutocomplete.searchInput": function(){
			if(!this.userAutocomplete.preventUpdate){
				if(this.userAutocomplete.searchTimeout != null){
					clearTimeout(this.userAutocomplete.searchTimeout);
				}
				var that = this;

				this.userAutocomplete.searchTimeout = setTimeout(function(){
					that.onAutocompleteInput(that.userAutocomplete.searchInput);
					that.userAutocomplete.searchTimeout = null;
				}, 500);
			}
			else {
				this.userAutocomplete.preventUpdate = false;
			}
		},
		"userAutocomplete.model": function(){
			this.userAutocomplete.preventUpdate = true;
			this.userAutocomplete.errors.splice(0, this.userAutocomplete.errors.length);
		}
	},

	methods: {
		open() {
			this.state = STATES.DEFAULT;
			var that = this;
			this.userAutocomplete.model = null;
			this.userAutocomplete.items.splice(0, this.userAutocomplete.items.length);

			this.$nextTick(function(){
				that.model = true;
			});

			this.onAutocompleteInput("");
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
				response = await this.$store.dispatch("userPasswords/searchShareForUser", {
					passwordCode: this.passwordCode,
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

		async onSubmit(){
			if (this.state == STATES.DEFAULT){
				this.userAutocomplete.errors.splice(0, this.userAutocomplete.errors.length);

				if(this.userAutocomplete.model == null || this.userAutocomplete.model == ""){
					this.userAutocomplete.errors.push("This field is required");
					return;
				}

				this.state = STATES.SAVING;

				let share = await this.$store.dispatch("userPasswords/sharePassword", {
					passwordCode: this.$route.params.password_id,
					userId: this.userAutocomplete.model
				});

				this.$emit("shareAdded", share);

				this.close();
			}
		}
	}
}
</script>

<style scoped>

</style>