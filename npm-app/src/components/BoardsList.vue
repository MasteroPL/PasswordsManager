<template>
	<div class="BoardsList" style="display: flex; flex-direction: column;">
		<h2 style="margin-top: 8px">Boards</h2>
		<v-divider style="margin-top: 8px"></v-divider>

		<template v-if="state == STATES.DEFAULT">
			<div class="BoardsList__boards" v-if="boards.length > 0">
				<v-card
					class="BoardList__boards-card"
					outlined
					v-for="item in boards"
					:key="item.id"

					@mouseover="item.hover = true"
					@mouseleave="item.hover = false"
					@click="onBoardCardClick(item)"
				>
					<v-icon
						v-if="item.isOwner"
						class="BoardList__board-owner-icon"
					>mdi-crown-circle</v-icon>

					<v-menu
						left
					>
						<template v-slot:activator="{ on, attrs }">
							<v-btn
								class="BoardList__boards-action"
								icon
								v-on:click.stop
								v-bind="attrs"
								v-on="on"
							>
								<v-icon>mdi-dots-vertical</v-icon>
							</v-btn>
						</template>

						<v-list>
							<v-list-item v-if="false"
								@click="onUnhideClick(item)"
							>
								<v-list-item-title>Unhide board</v-list-item-title>
								<v-list-item-icon>
									<v-icon>mdi-eye</v-icon>
								</v-list-item-icon>
							</v-list-item>
							<v-list-item v-else
								@click="onHideClick(item)"
							>
								<v-list-item-title>Hide board</v-list-item-title>
								<v-list-item-icon>
									<v-icon>mdi-eye-off</v-icon>
								</v-list-item-icon>
							</v-list-item>
							<v-list-item v-if="!item.isOwner"
								@click="onLeaveClick(item)"
							>
								<v-list-item-title>Leave board</v-list-item-title>
								<v-list-item-icon>
									<v-icon>mdi-exit-to-app</v-icon>
								</v-list-item-icon>
							</v-list-item>
							<v-list-item v-else
								@click="onDeleteClick(item)"
							>
								<v-list-item-title style="color:red">Delete board</v-list-item-title>
								<v-list-item-icon>
									<v-icon style='color:red'>mdi-delete</v-icon>
								</v-list-item-icon>
							</v-list-item>
						</v-list>
					</v-menu>
				
					<v-card-text

					>
						<p 
							style="padding-right: 24px; overflow: hidden; text-overflow: ellipsis;"
							class="text-h6 text--primary BoardsList__boards-card__title"
						>
							{{ item.name }}
						</p>
						<div class="BoardsList__boards-card__description">
							<template v-if="item.description != null">
								{{ item.description }}
							</template>
							<template v-else>
								No description
							</template>
						</div>
					</v-card-text>

					<v-expand-transition

					>
						<v-card
							:elevation="0"
							v-if="item.hover"
							class="transition-fast-in-fast-out v-card--reveal"
							style="height: 100%"
						>
							<div class="BoardsList__boards-card__click-to-open">
								Click to go to the board
							</div>
						</v-card>
					</v-expand-transition>
				</v-card>
			</div>

			<div 
				style="flex: 1 1 auto;"
				v-else
			>
				<div style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center">
					<div style="text-align: center;">
						<v-icon style="font-size: 64px; margin-bottom: 16px;">mdi-view-dashboard</v-icon>

						<h3>No boards found</h3>
						<p>You are not assigned to any boards</p>
					</div>
				</div>
			</div>

			<v-btn
				color="secondary"
				dark
				fab
				large
				class="BoardList__add-board-button"
				@click="onBoardAddClick()"
			>
				<v-icon>mdi-plus</v-icon>
			</v-btn>
		</template>

		<v-container style="flex: 1 1 auto;"
			v-if="state == STATES.LOADING"
		>
			<div style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center;">
				<v-progress-circular
					style="margin: 0 auto; text-align:center;"
					:size="64"
					color="primary"
					indeterminate
				></v-progress-circular>
			</div>
		</v-container>


		<GenericDeleteBoardDialog
			ref="GenericDeleteBoardDialog"
			:boardId="deleteBoardDialog.boardId"
			:boardName="deleteBoardDialog.boardName"

			@deleted="onDeleted()"
		></GenericDeleteBoardDialog>

		<GenericLeaveBoardDialog
			ref="GenericLeaveBoardDialog"
			:boardId="leaveBoardDialog.boardId"
			:boardName="leaveBoardDialog.boardName"

			@left="onLeft()"
		></GenericLeaveBoardDialog>
	</div>
</template>

<script>
const NO_CACHE = true;
const STATES = {
	INITIAL: 0, // before loading data
	DEFAULT: 1, // after loading data
	LOADING: 2 // during loading data
};

import ERRORS from '@/consts/standardErrors.js'
import GenericDeleteBoardDialog from '@/generic/GenericDeleteBoardDialog.vue'
import GenericLeaveBoardDialog from '@/generic/GenericLeaveBoardDialog.vue'

export default {
	name: "BoardsList",

	components: {
		"GenericDeleteBoardDialog": GenericDeleteBoardDialog,
		"GenericLeaveBoardDialog": GenericLeaveBoardDialog
	},

	data: () => ({
		state: STATES.INITIAL,
		getDataTimeout: null,
		boards: [
			// {
			// 	id: {Number},
			// 	name: {String},
			// 	description: {String},
			// 	isOwner: {Boolean},
			// 	isAdmin: {Boolean},
			// 	hover: {Boolean}
			// },
		],
		deleteBoardDialog: {
			boardId: -1,
			boardName: null
		},
		leaveBoardDialog: {
			boardId: -1,
			boardName: null
		}
	}),

	computed: {
		STATES() {
			return STATES;
		}
	},

	async mounted() {
		await this.getData();
	},
	methods: {
		onHideClick(item){
			console.log(item);
		},
		onUnhideClick(item){
			console.log(item);
		},
		onLeaveClick(item){
			this.leaveBoardDialog.boardId = item.id;
			this.leaveBoardDialog.boardName = item.name;

			this.$refs.GenericLeaveBoardDialog.open();
		},
		onDeleteClick(item){
			this.deleteBoardDialog.boardId = item.id;
			this.deleteBoardDialog.boardName = item.name;

			this.$refs.GenericDeleteBoardDialog.open();
		},
		onBoardAddClick(){
			this.$router.push("/boards/new/");
		},
		onDeleted(){
			this.adaptStoreData();
		},
		onLeft(){
			this.adaptStoreData();
		},

		adaptStoreData(){
			let storeData = this.$store.getters["boardsList/getBoardsSortedByName"];
			this.boards.splice(0, this.boards.length);
			let item = null;

			if(storeData != null){
				for(let i = 0; i < storeData.length; i++){
					item = storeData[i];
					this.boards.push({
						...item,
						hover: false // internal view logic
					});
				}
			}
		},

		async getData(){
			var that = this;
			if(this.getDataTimeout != null){
				clearTimeout(this.getDataTimeout);
			}

			// If request take long enough, show loading spinner
			this.getDataTimeout = setTimeout(function(){
				that.state = STATES.LOADING;
				that.getDataTimeout = null;
			}, 200);

			try {
				await this.$store.dispatch("boardsList/getData", NO_CACHE);
			} catch(error){
				console.log(error);
				switch(error.type){
					case ERRORS.UNAUTHORIZED:
						this.$router.push("/login/");
						break;

					case ERRORS.FORBIDDEN:
						this.$router.push("/login/");
						break;

					case ERRORS.NETWORK_ERROR:
						// TODO
						break;

					default:
						// TODO
						break;
				}
			}

			this.adaptStoreData();

			if(this.getDataTimeout != null){
				clearTimeout(this.getDataTimeout);
				this.getDataTimeout = null;
			}

			this.state = STATES.DEFAULT;
		},

		onBoardCardClick(item){
			this.$router.push({
				name: 'board',
				params: {
					board_id: item.id,
					isAdmin: item.isAdmin
				}
			});
		}
	}
}
</script>

<style scoped>
.BoardsList {
	padding: 16px;
	max-width: 1024px;
	height: 100%;
}

.BoardsList__boards {
	margin-top: 16px;
	padding-bottom: 64px;
}

.BoardList__boards-card {
	width: calc(33.33333% - 10px);
	margin-right: 15px;
	margin-bottom: 15px;
	display: inline-block;
	user-select: none;
}

.BoardList__boards-card:nth-child(3n) {
	margin-right: 0;
}

.BoardList__boards-card:focus::before {
	opacity: 0 !important;
}

.BoardsList__boards-card__title {
	margin-bottom: 0;
	max-width: 100%;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.BoardsList__boards-card__description {
	display: -webkit-box;
	-webkit-line-clamp: 4;
	-webkit-box-orient: vertical;
	overflow: hidden;
	max-width: 100%;
	height: 100px;
	max-height: 90px;
}

.v-card--reveal {
  bottom: 0;
  opacity: 0.9 !important;
  position: absolute;
  width: 100%;
}

.BoardsList__boards-card__click-to-open {
	display: flex;
	flex-direction: column;
	justify-content: center;
	width: 100%;
	height: 100%;
	padding: 8px;
	text-align: center;
	font-size: 18px;
	font-weight: bold;
}

.BoardList__boards-action {
	z-index: 1;
	position: absolute;
	right: 4px;
	top: 8px;
}

.BoardList__board-owner-icon {
	position: absolute;
	right: -10px;
	top: -10px;
	z-index: 1;
}

.BoardList__add-board-button {
	position: fixed;
	bottom: 16px;
	right: calc(100% - 1264px);
	z-index: 2;
}

@media screen and (max-width: 1296px){
	.BoardList__add-board-button {
		right: 16px;
	}
}

@media screen and (max-width: 700px){
	.BoardList__boards-card {
		width: calc(50% - 7.5px);
	}
	.BoardList__boards-card:nth-child(3n) {
		margin-right: 15px;
	}
	.BoardList__boards-card:nth-child(2n) {
		margin-right: 0;
	}
}

@media screen and (max-width: 420px) {
	.BoardList__boards-card {
		width: 100%;
		margin-right: 0;
	}
}
</style>