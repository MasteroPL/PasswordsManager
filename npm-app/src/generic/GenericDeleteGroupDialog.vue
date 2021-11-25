<template>
	<v-dialog
		v-model="model"
		max-width="320px"
	>
		<v-card
		>
			<v-card-title>Delete group</v-card-title>
			<v-divider></v-divider>

			<v-card-text style="padding-top: 20px;">
				<p
					style="font-size: 16px;"
				>Group chosen for deletion: <br /><b>{{ this.groupName }}</b></p>

				<v-checkbox
					color="secondary"
					style='margin-top:0; height: 28px'
					v-model="deletePasswords"
					label="Delete group passwords"
				></v-checkbox>

				<div 
					class="generic-delete-group-dialog__expansion-panel"
					:style="(deletePasswords) ? 'height: 0; padding-top: 0' : 'height: 76px'" 
				>
					<v-select
						v-model="groupSelectModel"
						color="secondary"
						outlined
						item-text="name"
						item-value="id"
						:items="groups"
						label="Move passwords to group"
					></v-select>
				</div>
			</v-card-text>

			<v-divider></v-divider>

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
					@click="confirmationDialog=true"
				>Delete</v-btn>
			</v-card-actions>
		</v-card>

	<v-dialog
		v-model="confirmationDialog"
		persistent
		width="300"
	>
		<v-card>
			<v-card-title>
				Are you sure?
			</v-card-title>

			<v-divider></v-divider>

			<v-card-text style="padding-top: 20px">
			<p>Are you sure you want to delete the group <b>{{ this.groupName }}</b><span v-if="deletePasswords"> and all of its passwords</span>?</p>

				<p style="margin-bottom: 0">This action <b><u>cannot be undone</u></b>!</p>
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
					@click="confirmationDialog = false; model = false;"
				>
					CANCEL
				</v-btn>
				<v-btn
					color="red"
					text
				>
				DELETE
			</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>


	</v-dialog>
</template>

<script>
export default {
	name: "GenericDeleteGroupDialog",
	props: {
		groupId: {
			type: Number,
			required: true
		},
		groupName: {
			type: String,
			required: true
		},
		definedGroups: {
			type: Array,
			required: true
		}
	},
	data: () => ({
		model: false,
		confirmationDialog: false,
		deletePasswords: false,
		groupSelectModel: null,
		groups: [],
		loader: false
	}),
	methods: {
		init(){
			this.groups.splice(0, this.groups.length);

			if(this.definedGroups != null){
				for(let i = 0; i < this.definedGroups.length; i++){
					if(this.definedGroups[i].id != this.groupId){
						this.groups.push(this.definedGroups[i]);
					}
				}
			}
		},

		open(){
			this.init();
			var that = this;
			if(this.groupSelectModel == null){
				this.groupSelectModel = this.groups[0].id;
			}
			this.$nextTick(function(){
				that.model = true;
			});
		}
	}
}
</script>

<style scoped>
.generic-delete-group-dialog__expansion-panel{
	margin-top: 4px;
	padding-top: 16px;
	overflow-y: hidden;
	transition: height 0.1s ease-in-out, padding-top 0.1s ease-in-out;
}
</style>