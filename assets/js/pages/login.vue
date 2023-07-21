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
              <v-form @submit.prevent="connect">
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
                <v-btn 
                  type="submit" 
                  class="mx-auto mt-5 btn--connect"
                  >
                  Login
                </v-btn>
                <p class="c-o" v-if="invalid">{{message}}</p>
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
import { login } from '@/services/authentification.js';

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
            invalid:false,
        };
    },
    beforeMount: async function () {
        this.users= this.$root.$data.tab ;
        console.log("data from django",this.users);
    },
    methods: {
      async connect()  {
            const params = {
                username: this.username,
                password: this.password,
            };
            login(params).then((resp) => {
              this.invalid = false ;
              console.log("retour from api" ,resp);
               window.location.href = `/dashboard`;
            }).catch((err) => {
                if (err.response && err.response.status === 401) {
                  const responseData = err.response.data; // Access the response data
                  console.log("401 Error Response:", responseData);
                  this.invalid = true ;
                  this.message=responseData.message;
                  // Handle the 401 error here
                } else {
                  console.error("Error occurred:", error);
                  // Handle other errors
                }
            });
        
      },
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