<template>
  <v-app-bar>
    <v-toolbar>
      <v-toolbar-title class="ml-8">
        <img src="../assets/images/logo.svg" alt="logo" height="50" />
      </v-toolbar-title>
      <v-spacer />
      <v-menu offset-y>
        <template v-slot:activator="{ on }">
          <v-avatar class="ml-3 mr-3" size="30" v-on="on">
            <v-icon size="30" class=" white--text" color="white">mdi-account-circle-outline</v-icon>
          </v-avatar>
        </template>
        <v-list>
          <v-list-item>
            <v-btn text>Profile</v-btn>
          </v-list-item>
          <v-list-item>
            <v-btn text>Settings</v-btn>
          </v-list-item>
          <v-list-item>
            <v-list-item-title>
              <v-btn @click="logout" text>Logout</v-btn>
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    
      <div style="display: flex; flex-direction: column; margin-right: 10px; margin-left: 10px;">
        <span style="color: white;">{{ userName }}</span>
        <span style="color: white;">{{ email}}</span>
      </div>

      <br />
    </v-toolbar>
  </v-app-bar>
</template>

<script>
export default {
  name: "ToolbarComponent",
  data() {
    return {
      userName: null,
      email: null,
    };
  },
  mounted() {
    let retriveInfo = localStorage.getItem("userInfo");
    this.user = JSON.parse(retriveInfo);
    this.userName = this.user.username;
    this.email = this.user.email;
  },
};
</script>

<style scoped>
.v-toolbar {
  background-color: #193286;
  /* color: #fff;
  font-family: Opens;
  font-size: 18px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  height: 70px; */
}
</style>
