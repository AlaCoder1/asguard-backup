<template>
  <v-app-bar>
    <v-toolbar>
      <v-toolbar-title class="ml-8">
        <img src="../assets/images/logo.svg" alt="logo" height="50" />
      </v-toolbar-title>
      <v-spacer />
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-avatar class="ml-3 mr-3" size="30" v-bind="props">
            <v-icon size="30" class="white--text" color="white"
              >mdi-account-circle-outline</v-icon
            >
          </v-avatar>
        </template>
        <v-list style="cursor: pointer; padding: 15px">
          <v-list-item> Profile </v-list-item>
          <v-list-item> Settings </v-list-item>

          <v-list-item> <span @click="logout">Logout</span> </v-list-item>
        </v-list>
      </v-menu>

      <div class="userInfo">
        <span class="white-color">{{ state.currentInfo.username }}</span>
        <span class="white-color">{{ state.currentInfo.email }}</span>
      </div>

      <br />
    </v-toolbar>
  </v-app-bar>
</template>

<script>
import axios from "axios";
import { reactive, onMounted } from "vue";
export default {
  name: "ToolbarComponent",

  setup() {
    onMounted(() => {
      let retriveInfo = localStorage.getItem("user-info");
      let userInfo = JSON.parse(retriveInfo);
      let user = userInfo;
      state.currentInfo = { ...user.currentUser };
    });
    const state = reactive({
      currentInfo: {},
    });

    const logout = async () => {
      try {
        await axios.get("/auth/logout");
        window.location.href = "/";
      } catch (error) {
        console.error("Error during logout:", error);
      }
    };

    return {
      state,
      logout,
    };
  },
};
</script>

<style scoped>
.userInfo {
  display: flex;
  flex-direction: column;
  margin-right: 10px;
  margin-left: 10px;
}

.white-color {
  color: white;
}

.v-toolbar {
  background-color: #193286;
  color: white;
  font-size: 18.16px;
  font-family: Nunito;
  font-weight: 400;
  word-wrap: break-word;
}
</style>
