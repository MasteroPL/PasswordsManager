<template>
	<v-dialog
		v-model="model"
		max-width="320"
	>
		<v-card>
			<v-card-title>
				Leave board
			</v-card-title>

			<v-divider></v-divider>

			<v-card-text style="padding-top: 20px">
				<span v-if="boardName != null">
					Are you sure you want to leave board "<b>{{ boardName }}</b>"?
				</span>

				<span v-else>
					Are you sure you want to leave this board?
				</span>
			</v-card-text>

			<v-progress-linear
				:active="state == STATES.LOADING"
				indeterminate
				color="primary"
			></v-progress-linear>

			<v-divider></v-divider>

			<v-card-actions>
				<v-spacer></v-spacer>

				<v-btn
					text
					@click="model=false"
					:disabled="disableControls"
				>CANCEL</v-btn>

				<v-btn
					text
					color="red"
					@click="onSubmitClick()"
					:disabled="disableControls"
				>LEAVE</v-btn>
			</v-card-actions>
		</v-card>

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

	</v-dialog>
</template>

<script>
import ERRORS from '@/consts/standardErrors.js'

const STATES = {
	DEFAULT: 0,
	LOADING: 1
};

export default {
	name: "GenericLeaveBoardDialog",
	
	props: {
		boardId: {
			type: Number,
			required: true
		},
		boardName: {
			type: String,
			required: false,
			default: null
		}
	},

	computed: {
		STATES: () => {
			return STATES;
		}
	},
	
	data: () => ({
		model: false,
		state: STATES.DEFAULT,
		disableControls: false,

		submitTimeout: null,

		errorDialog: {
			model: false,
			title: "An error occured",
			description: "An unknown error occured, please try again later"
		}
	}),

	mounted() {

	},

	methods: {
		open(){
			var that = this;
			this.$nextTick(function(){
				if(that.boardId != -1){
					that.disableControls = false;
					that.state = STATES.DEFAULT;
					that.model = true;
				}
			});
		},
		close() {
			this.model = false;
		},
		async onSubmitClick(){
			if(this.boardId != -1){
				this.disableControls = true;
				let boardId = this.boardId;

				var that = this;
				if(this.submitTimeout != null){
					clearTimeout(this.submitTimeout);
				}
				this.submitTimeout = setTimeout(function(){
					that.state = STATES.LOADING;
					that.submitTimeout = null;
				}, 200);

				let exception = false;
				try {
					await this.$store.dispatch("boardsList/leaveBoard", { id: this.boardId });
				} catch (error){
					exception = true;
					switch(error.type){
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
					this.state = STATES.DEFAULT;
				}

				if (exception){
					this.disableControls = false;
					return;
				}

				this.close();
				this.$emit('left', boardId);
			}
		}
	}
}
</script>