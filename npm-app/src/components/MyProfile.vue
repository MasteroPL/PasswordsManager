<template>
	<div class="my-profile-container" style="height: 100%; padding-top: 18px; display: flex; flex-direction: column;">
		<h2 style="padding-bottom: 16px; ">My profile</h2>

		<v-divider></v-divider>

		<v-list style="background: none; padding-top: 0">
			<v-subheader
			>PREFERENCES</v-subheader>
			<v-divider></v-divider>

			<v-list-item>
				<v-switch
					v-model="darkModeSwitch"
					inset
					color="secondary"
					:label="`Dark mode ${(darkModeSwitch) ? 'enabled' : 'disabled'}`"
				></v-switch>
			</v-list-item>

			<v-divider></v-divider>
			
			<v-subheader
			>SECURITY</v-subheader>

			<v-divider></v-divider>

			<v-list-item
				@click="onChangePasswordClick()"
			>
				Change password
			</v-list-item>

			<v-divider></v-divider>
		</v-list>
	</div>
</template>

<script>
export default {
	name: "MyProfile",

	data: () => ({
		darkModeSwitch: true
	}),
	mounted(){
		var value = localStorage.getItem('theme');
		if(value != null && value == "dark"){
			this.darkModeSwitch = true;
		}
		else{
			this.darkModeSwitch = false;
		}
	},

	watch: {
		darkModeSwitch: function(){
			this.$emit('set-dark-mode', this.darkModeSwitch);
		}
	},

	methods: {
		onChangePasswordClick(){
			this.$router.push("/change-password/");
		}
	}
}
</script>

<style scoped>
.my-profile-container {
	max-width: 600px;
	padding-left: 16px;
	padding-right: 16px;
}
</style>