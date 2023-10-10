<template>
    <v-app id="inspire">
        <!-- <base-layout title="User & certificat management" >
            <template #content> -->
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
                                            <user-management :DataList="{'groups': groups, 'users': users}" />
                                        </v-col>

                                        <!-- <v-col cols="6" style="height: 100%;">
                                            <network-server-management :DataList="servers" />
                                        </v-col> -->

                                        <v-col cols="6" style="height: 100%;">
                                            <group-management  :DataList="groups" />
                                        </v-col>
                                    </v-row>

                                    <v-row no-gutters align="center" style = "overflow: hidden;"
                                        class=" pr-4 axe-media-print-hide axe-sticky-three mt-10">
                                        <!-- <v-col cols="6" style="height: 100%;">
                                            <group-management  :DataList="groups" />
                                        </v-col> -->
                                        <v-col cols="6" style="height: 100%;">
                                        </v-col>
                                    </v-row>

                                </v-tab-item>
                                <v-tab-item :value="'certificats-management'" :transition="false">
                                    <v-row no-gutters class=" pr-4 axe-media-print-hide axe-sticky-three"
                                        style="width: calc(130vh);" aria-label="certificats-management" align="center">
                                        <v-col cols="12" style="height: 100%;">
                                            <certificats-management  />
                                        </v-col>
                                    </v-row>
                                </v-tab-item>
                            </v-tabs-items>
                        </v-col>
                    </v-row>
                </v-container>
            <!-- </template>
        </base-layout> -->
    </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';
import UserManagement from '@/pages/user-management.vue';
import GroupManagement from '@/pages/group-management.vue';
import NetworkServerManagement from '@/pages/network-server-management.vue';
import CertificatsManagement from '@/pages/certificats-management.vue';

export default {
    name: 'HomeComponent',
    components: {
        BaseLayout,
        UserManagement,
        NetworkServerManagement,
        GroupManagement,
        CertificatsManagement,
    },

    data() {
        return {
            tab: null,
            users: [],
            groups: [],
            servers: [],
        };
    },
    methods: {
        setData(Array_String) {
            const validJsonString = Array_String
                .replace(/'/g, '"')
                .replace(/True/g, 'true')
                .replace(/False/g, 'false')
                .replace(/None/g, 'null');

            const parsedArray = JSON.parse(validJsonString);

            // this.users = parsedArray;
            // console.log("parsedarray :"+parsedArray)

            return parsedArray;
        },
        // ... other methods
    },
    beforeMount: async function () {
        console.log("before mount data.users :"+JSON.stringify (this.$root.$data.users));

        //   parsing users data
        let parsedData = this.setData(this.$root.$data.users);

        this.users = parsedData;
        //   parsing users data


        //   parsing groups data
        let parsedgroupsData = this.setData(this.$root.$data.groups);

        this.groups = parsedgroupsData;
        //   parsing groups data


        // //   parsing servers data
        let parsedserversData = this.setData(this.$root.$data.servers);

        this.servers = parsedserversData;
        // //   parsing servers data


    }
};
</script>

