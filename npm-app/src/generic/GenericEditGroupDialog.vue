<template>
	<v-dialog
		max-width="500"
		v-model="model"
		persistent
	>
		<v-card>
			<v-card-title v-if="groupId == null">Add group</v-card-title>
			<v-card-title v-else>Edit group</v-card-title>

			<v-divider></v-divider>

			<v-card-text style="padding-top: 24px">
				<v-text-field
					outlined
					v-model="groupName"
					label="Group name"
					color="secondary"
				></v-text-field>

				<v-textarea
					outlined
					v-model="groupDescription"
					label="Group description"
					color="secondary"
				></v-textarea>

				<v-select
					v-model="groupPosition"
					outlined
					item-text="name"
					item-value="id"
					:items="groups"
					:label="(this.groupId == null) ? 'Add group below' : 'Move group below'"
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
				>CONFIRM</v-btn>
			</v-card-actions>

		</v-card>
	</v-dialog>
</template>

<script>
export default {
	name: "GenericEditGroupDialog",
	props: {
		groupId: {
			type: Number,
			required: false,
			default: null
		},
		defaultGroupName: {
			type: String,
			required: false,
			default: null
		},
		defaultGroupDescription: {
			type: String,
			required: false,
			default: null
		},
		defaultGroupPosition: {
			type: String,
			required: false,
			default: null
		},
		definedGroups: {
			type: Array,
			required: true
		}
	},
	data: () => ({
		model: false,
		groupName: null,
		groupDescription: null,
		groupPosition: null,
		loader: false,
		groups: []
	}),
	mounted() {

	},
	methods: {
		init() {
			this.groups.splice(0, this.groups.length);

			this.groups.push({
				id: -50,
				name: "-------",
				default: false
			});

			if(this.definedGroups != null){
				for(let i = 0; i < this.definedGroups.length; i++){
					if(this.definedGroups[i].id != this.groupId){
						this.groups.push(this.definedGroups[i]);
					}
				}
			}

			this.groupdName = this.defaultGroupName;
			this.groupDescription = this.defaultGroupDescription;
			this.groupPosition = this.defaultGroupPosition;

			if(this.groupPosition == null){
				this.groupPosition = this.groups[0].id
			}
		},

		open(){
			this.init();

			var that = this;
			this.$nextTick(function(){
				that.model = true;
			});
		}
	}
}
</script>

<style scoped>

</style>