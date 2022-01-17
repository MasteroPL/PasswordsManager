<template>
	<div class="board-groups-edit" style="height: 100%; padding-top: 12px; display: flex; flex-direction: column;">
		<div class="board-groups-edit__back">
			<v-btn
				text
				style="padding-left: 4px;"
				@click="onBackClick()"
			>
				<v-icon>mdi-chevron-left</v-icon>
				Back
			</v-btn>
		</div>

		<div v-if="state == STATES.DEFAULT">
			<div class="board-groups-edit__add-new" style="text-align:right">
				<v-btn
					color="primary"
					@click="onTabAddClick()"
				>
					Add tab
					<v-icon
						right
					>mdi-plus</v-icon>
				</v-btn>
			</div>

			<v-list
				class="board-groups-edit__group-list"
			>
				<template
					v-for="item in tabsList"
				>
					<v-list-item
						:key="item.id"
					>
						<v-list-item-content>
							<v-list-item-title>{{ item.name }}</v-list-item-title>
							<v-list-item-subtitle>Passwords: {{ item.passwordsCount }}</v-list-item-subtitle>
							<v-list-item-subtitle
								v-if="item.default"
							>Default tab</v-list-item-subtitle>
						</v-list-item-content>

						<v-list-item-action>
							<v-btn
								icon
								color="secondary"
								@click="onTabEditClick(item)"
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
						v-if="item.id != tabsList[tabsList.length - 1].id"
						:key="'divider-' + item.id"
					></v-divider>
				</template>
			</v-list>
		</div>

		<v-container style="flex: 1 1 auto;"
			v-if="state == STATES.LOADING"
		>
			<div style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
				<v-progress-circular
					style="margin: 0 auto; text-align:center;"
					:size="64"
					color="primary"
					indeterminate
				></v-progress-circular>
			</div>
		</v-container>

		<GenericDeleteTabDialog
			ref="GenericDeleteTabDialog"
			:tabId="deleteTabDialog.tabId"
			:tabName="deleteTabDialog.tabName"
			:definedTabs="tabsList"

			@deleted="onTabsChange()"
		></GenericDeleteTabDialog>

		<GenericEditTabDialog
			ref="GenericEditTabDialog"
			:definedTabs="tabsList"
			:tabId="editTabDialog.tabId"
			:defaultTabName="editTabDialog.tabName"
			:defaultTabPosition="editTabDialog.tabPosition"

			@added="onTabsChange()"
			@edited="onTabsChange()"
		></GenericEditTabDialog>
	</div>
</template>


<script>
import GenericDeleteTabDialog from "@/generic/GenericDeleteTabDialog.vue"
import GenericEditTabDialog from "@/generic/GenericEditTabDialog.vue"

const STATES = {
	INITIAL: 0,
	DEFAULT: 1,
	LOADING: 2
};

export default {
	name: "BoardGroupsEdit",

	components: {
		"GenericDeleteTabDialog": GenericDeleteTabDialog,
		"GenericEditTabDialog": GenericEditTabDialog
	},

	data: () => ({
		state: STATES.INITIAL,
		loadingTimeout: null,

		tabsList: [
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
		ungroupedPasswordsCount: 5,
		editTabDialog: {
			tabId: null,
			tabName: null,
			tabPosition: null
		},
		deleteTabDialog: {
			tabId: null,
			tabName: null
		}
	}),
	computed: {
		STATES: function(){
			return STATES;
		}
	},
	async mounted() {
		await this.loadData();
	},
	methods: {
		adaptStoreData(){
			let board = this.$store.getters["board/getBoard"];

			if(board != null){
				let tabs = board.tabs;

				this.tabsList.splice(0, this.tabsList.length);
				let obj = null;
				console.log(tabs);
				for(let i = 0; i < tabs.length; i++){
					obj = {
						id: tabs[i].id,
						name: tabs[i].name,
						default: tabs[i].isDefault,
						passwordsCount: tabs[i].passwords.length,
						belowTab: (i > 0) ? tabs[i-1].id : null
					};
					this.tabsList.push(obj);
				}
			}
			else{
				this.tabsList = {};
			}
		},

		async loadData(){
			var that = this;
			if(this.loadingTimeout != null){
				clearTimeout(this.loadingTimeout);
			}
			this.loadingTimeout = setTimeout(function(){
				that.state = STATES.LOADING;
				that.loadingTimeout = null;
			});

			try {
				await this.$store.dispatch("board/getData", {
					id: this.$route.params.board_id,
					allowCache: true
				});
			} catch(error){
				console.log(error);
				return;
			}

			this.adaptStoreData();
			if(this.loadingTimeout != null){
				clearTimeout(this.loadingTimeout);
			}
			this.loadingTimeout = null;
			this.state = STATES.DEFAULT;
		},

		onBackClick(){
			this.$router.push("/board/" + this.$route.params.board_id);
		},

		onTabAddClick(){
			this.editTabDialog.tabId = null;
			this.editTabDialog.tabName = null;
			this.editTabDialog.tabPosition = null;

			this.$nextTick(function(){
				this.$refs.GenericEditTabDialog.open();
			});
		},

		onTabEditClick(groupItem){
			this.editTabDialog.tabId = groupItem.id;
			this.editTabDialog.tabName = groupItem.name;
			this.editTabDialog.tabPosition = groupItem.belowTab;

			this.$nextTick(function(){
				this.$refs.GenericEditTabDialog.open();
			});
		},
		onGroupDeleteClick(groupItem){
			this.deleteTabDialog.tabId = groupItem.id;
			this.deleteTabDialog.tabName = groupItem.name;

			this.$nextTick(function(){
				this.$refs.GenericDeleteTabDialog.open();
			});
		},

		onTabsChange(){
			this.loadData();
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