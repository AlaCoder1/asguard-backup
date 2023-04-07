<template>
    <v-container>
    <v-row align="center" justify="center" style="justify-content: center;">
      <v-col cols="12" sm="7" md="5" class="text-center" justify="center">
            <v-img
                src="../../images/logoDMS.png"  height="100"
            />  

        <v-card class="mt-5">
          <v-card-text>
            <v-form @submit.prevent="login">
              <v-text-field
                v-model="username"
                label="Username"
                required
                outlined
              ></v-text-field>
              <v-text-field
                v-model="password"
                label="Password"
                required
                outlined
                type="password"
              ></v-text-field>
              <v-btn type="submit"  style="background-color: #FFC300;" class="mx-auto mt-5 btn--color">
                Login
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>


<script>


export default {
    name: 'HomeComponent',
    data() {
        return {
            users:'',
            test:[],
        };
    },
    beforeMount: async function () {
        this.users= this.$root.$data.tab ;
        console.log("out data from django",this.users);
    }
};
</script>
<style scoped>
.bg-color {
  background-color: #042439;
}
.btn--color {
  color: #FFFFFF;
    background-color!important: #FFC300;

}
</style>