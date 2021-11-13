<template>
	<div class="board-groups-edit">
		<div class="board-groups-edit__back">
			<v-btn
				text
				style="padding-left: 4px;"
			>
				<v-icon>mdi-chevron-left</v-icon>
				Back
			</v-btn>
		</div>

		<div class="board-groups-edit__add-new" style="text-align:right">
			<v-btn
				color="primary"
			>
				Add group
				<v-icon
					right
				>mdi-plus</v-icon>
			</v-btn>
		</div>

		<v-list
			class="board-groups-edit__group-list"
		>
			<template
				v-for="item in groupList"
			>
				<v-list-item
					:key="item.id"
				>
					<v-list-item-content>
						<v-list-item-title>{{ item.name }}</v-list-item-title>
						<v-list-item-subtitle>Passwords: {{ item.passwordsCount }}</v-list-item-subtitle>
						<v-list-item-subtitle
							v-if="item.default"
						>Defaut group</v-list-item-subtitle>
					</v-list-item-content>

					<v-list-item-action>
						<v-btn
							icon
							color="secondary"
							@click="onGroupEditClick(item)"
						>
							<v-icon>mdi-pencil</v-icon>
						</v-btn>
					</v-list-item-action>
					<v-list-item-action>
						<v-btn
							icon
							color="red"
							@click="onGroupDeleteClick(item)"
							:disabled="item.default"
						>
							<v-icon>mdi-delete</v-icon>
						</v-btn>
					</v-list-item-action>
				</v-list-item>

				<v-divider 
					v-if="item.id != groupList[groupList.length - 1].id"
					:key="'divider-' + item.id"
				></v-divider>
			</template>
		</v-list>

		<GenericDeleteGroupDialog
			ref="GenericDeleteGroupDialog"
			:groupId="0"
			:groupName="'Test'"
			:definedGroups="groupList"
		></GenericDeleteGroupDialog>

		<GenericEditGroupDialog
			ref="GenericEditGroupDialog"
			:definedGroups="groupList"
		></GenericEditGroupDialog>
	</div>
</template>


<script>
import GenericDeleteGroupDialog from "@/generic/GenericDeleteGroupDialog.vue"
import GenericEditGroupDialog from "@/generic/GenericEditGroupDialog.vue"

export default {
	name: "BoardGroupsEdit",

	components: {
		"GenericDeleteGroupDialog": GenericDeleteGroupDialog,
		"GenericEditGroupDialog": GenericEditGroupDialog
	},

	data: () => ({
		groupList: [
			{
				id: -2,
				name: "Group 1",
				passwordsCount: 25,
				default: false
			},
			{
				id: -3,
				name: "Group 2",
				passwordsCount: 13,
				default: false
			},
			{
				id: -1,
				name: "Not grouped",
				passwordsCount: 5,
				default: true
			}
		],
		ungroupedPasswordsCount: 5
	}),
	mounted() {
		//this.$refs.GenericEditGroupDialog.open();
	},
	methods: {
		onGroupEditClick(groupItem){
			console.log(groupItem);
		},
		onGroupDeleteClick(groupItem){
			console.log(groupItem);
		}
	}
}

</script>


<style scoped>
.board-groups-edit {
	max-width: 600px;
	padding-left: 8px;
	padding-right: 8px;
}

.board-groups-edit__group-list {
	background: none;
	background-color: none;
}
</style>