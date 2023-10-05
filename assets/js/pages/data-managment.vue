<template>
    <v-container class=" axe-media-print-hide" fluid>
        <v-row align="center" class=" pr-4 axe-media-print-hide axe-sticky-three">
            <v-col cols="12">
                <v-tabs v-model="tab" flat>
                    <v-tab href="#user-management">
                        User Management
                    </v-tab>
                    <v-tab href="#certificats-management">
                        Certificats Management
                    </v-tab>
                </v-tabs>
                <v-divider style="width: 100%" />

            </v-col>
        </v-row>
        <v-row>
            <v-col cols="12">
                <v-tabs-items v-model="tab">
                    <v-tab-item :value="'user-management'" :transition="false">
                        <v-row no-gutters align="center" class=" pr-4 axe-media-print-hide axe-sticky-three">
                            <v-col cols="6" style="height: 100%;">
                                <user-management :DataList="data" />
                            </v-col>
                            <v-col cols="6" style="height: 100%;">
                                <network-server-management :DataList="data" />
                            </v-col>
                        </v-row>
                        <v-row no-gutters align="center" class=" pr-4 axe-media-print-hide axe-sticky-three mt-10">
                            <v-col cols="6" style="height: 100%;">
                                <group-management :DataList="data" />
                            </v-col>
                            <v-col cols="6" style="height: 100%;">
                            </v-col>
                        </v-row>
                    </v-tab-item>
                    <v-tab-item :value="'certificats-management'" :transition="false">
                        <v-row no-gutters class=" pr-4 axe-media-print-hide axe-sticky-three" style="width: calc(130vh);"
                            aria-label="certificats-management" align="center">
                            <v-col cols="12" style="height: 100%;">
                                <certificats-management />
                            </v-col>
                        </v-row>
                    </v-tab-item>
                </v-tabs-items>

            </v-col>
        </v-row>
    </v-container>
</template>
  
<script>
import { Subscribe } from '../services/authentification';
import UserManagement from '@/pages/user-management.vue';
import GroupManagement from '@/pages/group-management.vue';
import NetworkServerManagement from '@/pages/network-server-management.vue';
import CertificatsManagement from '@/pages/certificats-management.vue';
import '@mdi/font/css/materialdesignicons.css'; // Import the MDI font CSS 

export default {
    name: "DataManagment",
    components: {
        UserManagement,
        NetworkServerManagement,
        GroupManagement,
        CertificatsManagement,
    },
    data() {
        return {
            tab: null,
            data: [],
        };
    },
    methods: {
        setData() {
            const validJsonString = this.$root.$data.tab
                .replace(/'/g, '"')
                .replace(/True/g, 'true')
                .replace(/False/g, 'false')
                .replace(/None/g, 'null');
            const parsedArray = JSON.parse(validJsonString);
            this.data = parsedArray;
        },
        async Subscribe(params) {
            // const params = {

            //     "status":true,

            // "subscription_id":1
            // };
            Subscribe(params).then((resp) => {
                // this.invalid = false ;
                console.log("retour from api", resp);
                //  window.location.href = `/dashboard`;
            }).catch((err) => {
                if (err.response && err.response.status === 401) {
                    const responseData = err.response.data; // Access the response data
                    console.log("401 Error Response:", responseData);
                    // this.invalid = true ;
                    this.message = responseData.message;
                    // Handle the 401 error here
                } else {
                    console.error("Error occurred:", error);
                    // Handle other errors
                }
            });

        },
    },
    beforeMount: async function () {
        this.setData();
        console.log("data provided is :"+JSON.stringify(this.data))
    }
};
</script>