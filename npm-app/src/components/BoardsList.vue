<template>
	<div class="BoardsList">
		<h2>Boards</h2>
		<v-divider style="margin-top: 8px"></v-divider>

		<div class="BoardsList__boards">
			<v-card
				class="BoardList__boards-card"
				outlined
				v-for="item in boards"
				:key="item.id"

				@mouseover="item.hover = true"
				@mouseleave="item.hover = false"
				@click="console.log('OK')"
			>
				<v-card-text

				>
					<p class="text-h6 text--primary BoardsList__boards-card__title">
						{{ item.name }}
					</p>
					<div class="BoardsList__boards-card__description">
						{{ item.description }}
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
	</div>
</template>

<script>
export default {
	name: "BoardsList",

	data: () => ({
		boards: [
			{
				id: 1,
				name: "Board 1",
				description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ante erat, vehicula eget fermentum at, tempus eu diam. Nam vehicula ligula mi, vitae mollis lorem blandit vitae.\n\nQuisque leo ligula, faucibus nec ligula tristique, efficitur dictum nisl. Etiam sit amet enim orci. Suspendisse nunc elit, posuere ac gravida id, volutpat at lectus. Nam tincidunt mauris quis lorem porta feugiat. Phasellus suscipit purus vel libero ultricies lacinia. Cras semper justo quis sapien pretium, sed efficitur elit lobortis. Quisque porta accumsan orci, sit amet volutpat ipsum.\n\nDonec fermentum bibendum magna, id consequat magna porttitor sit amet. Integer sodales odio ut justo lacinia, vitae cursus sapien ullamcorper. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In sodales est ut odio pellentesque dictum. Aliquam ultricies arcu nisl, gravida euismod mauris molestie non. Fusce est nisl, congue in velit vel, lacinia suscipit neque. ",
				hover: false
			},
			{
				id: 2,
				name: "Board 2",
				description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ante erat, vehicula eget fermentum at, tempus eu diam. Nam vehicula ligula mi, vitae mollis lorem blandit vitae.\n\nQuisque leo ligula, faucibus nec ligula tristique, efficitur dictum nisl. Etiam sit amet enim orci. Suspendisse nunc elit, posuere ac gravida id, volutpat at lectus. Nam tincidunt mauris quis lorem porta feugiat. Phasellus suscipit purus vel libero ultricies lacinia. Cras semper justo quis sapien pretium, sed efficitur elit lobortis. Quisque porta accumsan orci, sit amet volutpat ipsum.\n\nDonec fermentum bibendum magna, id consequat magna porttitor sit amet. Integer sodales odio ut justo lacinia, vitae cursus sapien ullamcorper. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In sodales est ut odio pellentesque dictum. Aliquam ultricies arcu nisl, gravida euismod mauris molestie non. Fusce est nisl, congue in velit vel, lacinia suscipit neque. ",
				hover: false
			},
			{
				id: 3,
				name: "Board 3",
				description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ante erat, vehicula eget fermentum at, tempus eu diam. Nam vehicula ligula mi, vitae mollis lorem blandit vitae.\n\nQuisque leo ligula, faucibus nec ligula tristique, efficitur dictum nisl. Etiam sit amet enim orci. Suspendisse nunc elit, posuere ac gravida id, volutpat at lectus. Nam tincidunt mauris quis lorem porta feugiat. Phasellus suscipit purus vel libero ultricies lacinia. Cras semper justo quis sapien pretium, sed efficitur elit lobortis. Quisque porta accumsan orci, sit amet volutpat ipsum.\n\nDonec fermentum bibendum magna, id consequat magna porttitor sit amet. Integer sodales odio ut justo lacinia, vitae cursus sapien ullamcorper. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In sodales est ut odio pellentesque dictum. Aliquam ultricies arcu nisl, gravida euismod mauris molestie non. Fusce est nisl, congue in velit vel, lacinia suscipit neque. ",
				hover: false
			},
			{
				id: 4,
				name: "Board 4",
				description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ante erat, vehicula eget fermentum at, tempus eu diam. Nam vehicula ligula mi, vitae mollis lorem blandit vitae.\n\nQuisque leo ligula, faucibus nec ligula tristique, efficitur dictum nisl. Etiam sit amet enim orci. Suspendisse nunc elit, posuere ac gravida id, volutpat at lectus. Nam tincidunt mauris quis lorem porta feugiat. Phasellus suscipit purus vel libero ultricies lacinia. Cras semper justo quis sapien pretium, sed efficitur elit lobortis. Quisque porta accumsan orci, sit amet volutpat ipsum.\n\nDonec fermentum bibendum magna, id consequat magna porttitor sit amet. Integer sodales odio ut justo lacinia, vitae cursus sapien ullamcorper. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In sodales est ut odio pellentesque dictum. Aliquam ultricies arcu nisl, gravida euismod mauris molestie non. Fusce est nisl, congue in velit vel, lacinia suscipit neque. ",
				hover: false
			},
			{
				id: 5,
				name: "Board 5",
				description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ante erat, vehicula eget fermentum at, tempus eu diam. Nam vehicula ligula mi, vitae mollis lorem blandit vitae.\n\nQuisque leo ligula, faucibus nec ligula tristique, efficitur dictum nisl. Etiam sit amet enim orci. Suspendisse nunc elit, posuere ac gravida id, volutpat at lectus. Nam tincidunt mauris quis lorem porta feugiat. Phasellus suscipit purus vel libero ultricies lacinia. Cras semper justo quis sapien pretium, sed efficitur elit lobortis. Quisque porta accumsan orci, sit amet volutpat ipsum.\n\nDonec fermentum bibendum magna, id consequat magna porttitor sit amet. Integer sodales odio ut justo lacinia, vitae cursus sapien ullamcorper. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In sodales est ut odio pellentesque dictum. Aliquam ultricies arcu nisl, gravida euismod mauris molestie non. Fusce est nisl, congue in velit vel, lacinia suscipit neque. ",
				hover: false
			},
			{
				id: 6,
				name: "Board 6",
				description: "Short description",
				hover: false
			}
		]
	}),

	mounted() {

	},
	methods: {

	}
}
</script>

<style scoped>
.BoardsList {
	padding: 16px;
	max-width: 1024px;
}

.BoardsList__boards {
	margin-top: 16px;
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