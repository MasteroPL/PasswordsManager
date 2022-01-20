<template>
	<div class="user-passwords-tabs-edit" style="height: 100%; padding-top: 12px; display: flex; flex-direction: column;">
		<div class="user-passwords-tabs__back">
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
			<div class="user-passwords-tabs__add-new" style="text-align:right">
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
				class="user-passwords-tabs__group-list"
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
			:boardMode="false"

			@deleted="onTabsChange()"
		></GenericDeleteTabDialog>

		<GenericEditTabDialog
			ref="GenericEditTabDialog"
			:definedTabs="tabsList"
			:tabId="editTabDialog.tabId"
			:defaultTabName="editTabDialog.tabName"
			:defaultTabPosition="editTabDialog.tabPosition"
			:boardMode="false"

			@added="onTabsChange()"
			@edited="onTabsChange()"
		></GenericEditTabDialog>
	</div>
</template>


<script>
import GenericDeleteTabDialog from "@/generic/GenericDeleteTabDialog.vue"
import GenericEditTabDialog from "@/generic/GenericEditTabDialog.vue"
import ERRORS from '@/consts/standardErrors'

const STATES = {
	INITIAL: 0,
	DEFAULT: 1,
	LOADING: 2
};

export default {
	name: "UserPasswordsTabsEdit",

	components: {
		"GenericDeleteTabDialog": GenericDeleteTabDialog,
		"GenericEditTabDialog": GenericEditTabDialog
	},

	data: () => ({
		state: STATES.INITIAL,
		loadingTimeout: null,

		tabsList: [
			// {
			// 	id: -2,
			// 	name: "Group 1",
			// 	passwordsCount: 25,
			// 	default: false
			// },
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
		adaptStoreData(storeData){
			let result = [];
			let tab = null;
			let previous = null;
			for(let i = 0; i < storeData.length; i++){
				tab = storeData[i];
				result.push({
					belowTab: previous,
					...tab
				});
				previous = tab.id;
			}
			return result;
		},

		async loadData(){
			let tabs;
			for(let i = 0; i < 2; i++){
				tabs = this.$store.getters["userPasswords/getTabs"];
				if (tabs != null){
					break;
				}

				try{
					await this.$store.dispatch("userPasswords/getData", {
						allowCache: false
					});
				} catch(error){
					if (error.type == ERRORS.UNAUTHORIZED || error.type == ERRORS.FORBIDDEN){
						this.$emit("logout");
						return;
					}
					throw error;
				}
			}

			if (tabs == null){
				this.$router.push("/user-passwords/");
				return;
			}

			this.tabsList = this.adaptStoreData(tabs);

			this.state = STATES.DEFAULT;
		},

		onBackClick(){
			this.$router.push("/user-passwords/");
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
.user-passwords-tabs-edit {
	max-width: 600px;
	padding-left: 8px;
	padding-right: 8px;
}

.user-passwords-tabs__group-list {
	background: none;
	background-color: none;
}
</style>