<template>
	<v-dialog
		max-width="350"
		v-model="model"
		persistent
	>
		<v-card>
			<v-card-title v-if="tabId == null">Add tab</v-card-title>
			<v-card-title v-else>Edit tab</v-card-title>

			<v-divider></v-divider>

			<v-card-text style="padding-top: 24px">
				<v-text-field
					outlined
					v-model="tabName"
					label="Tab name"
					color="secondary"
					:maxlength="30"
					counter
					:error-messages="tabNameErrors"
				></v-text-field>

				<v-select
					v-model="tabPosition"
					outlined
					item-text="name"
					item-value="id"
					:items="groups"
					:label="(this.tabId == null) ? 'Add group below' : 'Move group below'"
				></v-select>

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
					@click="model=false"
				>CANCEL</v-btn>

				<v-btn
					color="secondary"
					text
					@click="onSubmit()"
				>{{ (tabId != null) ? 'SAVE' : 'ADD' }}</v-btn>
			</v-card-actions>

		</v-card>
	</v-dialog>
</template>

<script>
export default {
	name: "GenericEditGroupDialog",
	props: {
		tabId: {
			type: Number,
			required: false,
			default: null
		},
		defaultTabName: {
			type: String,
			required: false,
			default: null
		},
		defaultTabPosition: {
			type: Number,
			required: false,
			default: null
		},
		definedTabs: {
			type: Array,
			required: true
		}
	},
	data: () => ({
		model: false,
		tabName: null,
		tabPosition: null,
		loader: false,
		groups: [],
		tabNameErrors: []
	}),
	mounted() {

	},
	methods: {
		init() {
			this.groups.splice(0, this.groups.length);

			this.groups.push({
				id: null,
				name: "-------",
				default: false
			});

			if(this.definedTabs != null){
				for(let i = 0; i < this.definedTabs.length; i++){
					if(this.definedTabs[i].id != this.tabId){
						this.groups.push(this.definedTabs[i]);
					}
				}
			}

			this.tabName = this.defaultTabName;
			this.tabPosition = this.defaultTabPosition;

			if(this.tabPosition == null){
				this.tabPosition = this.groups[0].id
			}
		},

		open(){
			this.init();

			var that = this;
			this.$nextTick(function(){
				that.model = true;
			});
		},

		close() {
			this.model = false;
		},

		async onSubmit() {
			this.tabNameErrors.splice(0, this.tabNameErrors.length);
			if(this.tabName == null || this.tabName == ""){
				this.tabNameErrors.push("This field is required");
				return;
			}

			// ADD NEW
			if(this.tabId == null){
				await this.$store.dispatch("board/addTab", {
					boardId: this.$route.params.board_id,
					tabName: this.tabName,
					addAfter: this.tabPosition
				});

				this.$emit("added");
				this.close();
			}

			// EDIT EXISTING
			else {
				await this.$store.dispatch("board/editTab", {
					boardId: this.$route.params.board_id,
					tabId: this.tabId,
					tabName: this.tabName,
					putAfter: this.tabPosition
				});

				this.$emit("edited");
				this.close();
			}
		}
	}
}
</script>

<style scoped>

</style>