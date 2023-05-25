<template>
  <div class="bg-color">
    <v-container class="dms-login-container">
      <v-row align="center" justify="center" style="justify-content: center;">
        <v-col cols="12" sm="7" md="5" class="text-center pos" justify="center">

              <img
                src="../../images/logoDMS.png"  
                height="100"
                class="img-center"
              />

          <div class="mt-5" >
              <v-form @submit.prevent="login">
              <p class="c-w">Username</p>
                <v-text-field
                  rounded
                  v-model="username"
                  label="Username"
                  required
                  class="input-w"
                ></v-text-field>
                <p class="c-w">Password</p>
                <v-text-field
                  rounded
                  v-model="password"
                  label="Password"
                  required
                  type="password"
                  class="input-w"
                ></v-text-field>
                <v-btn type="submit" class="mx-auto mt-5 btn--connect">
                  Login
                </v-btn>
                <p class="c-o">Wrong username or password!!!</p>
              </v-form>
          </div>
        </v-col>
      </v-row>
    </v-container>
    <Footer />
  </div>
</template>


<script>
import Footer from '@/components/layout/footer.vue';


export default {
    name: 'HomeComponent',
    components: {
        Footer,
    },
    data() {
        return {
            users:'',
            test:[],
            username:'',
            password:'',
        };
    },
    beforeMount: async function () {
        this.users= this.$root.$data.tab ;
        console.log("out data from django",this.users);
    }
};
</script>
<style scoped>

.btn--connect {
    color: #FFFFFF;
    background-color: #FFC300!important;
    display: block;
    margin-left: auto;
    margin-right: auto;
    margin-top: 5%;
    width:40%
}
.pos {
  transform: translateY(20%);
}
.img-center {
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 33%;
  height: 33%;
}
.input-w {
    background-color: white;
}
.c-w {
  color:white;
  margin-left: 10%;
}
.c-o {
  color:#FFC300;
  text-align:center;
  margin-top: 5%;
}
</style>