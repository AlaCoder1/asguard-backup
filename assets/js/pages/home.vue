<template>
    <v-app id="inspire">
        <base-layout title="home" active-menu="home">
            <template #content>
                <!-- <v-container class=" axe-media-print-hide" fluid>
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
                                            <network-server-management />
                                        </v-col>
                                    </v-row>
                                    <v-row no-gutters align="center"
                                        class=" pr-4 axe-media-print-hide axe-sticky-three mt-10">
                                        <v-col cols="6" style="height: 100%;">
                                            <group-management />
                                        </v-col>
                                        <v-col cols="6" style="height: 100%;">
                                        </v-col>
                                    </v-row>
                                </v-tab-item>
                                <v-tab-item :value="'certificats-management'" :transition="false">
                                    <v-row no-gutters class=" pr-4 axe-media-print-hide axe-sticky-three"
                                        style="width: calc(130vh);" aria-label="certificats-management" align="center">
                                        <v-col cols="12" style="height: 100%;">
                                            <certificats-management />
                                        </v-col>
                                    </v-row>
                                </v-tab-item>
                            </v-tabs-items>
                        </v-col>
                    </v-row>
                </v-container> -->
            </template>
        </base-layout>
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
    computed: {
        message() {
        return this.$store.state.count;
        },
    },
    data() {
        return {
            tab: null,
            data: [],
            users: '',
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
        incrementCount() {
            this.$store.commit('incrementCount');
        },
        // ... other methods
    },
    beforeMount: async function () {
        console.log("suii mounted :" + JSON.stringify(this.$root.$data.tab));
        this.incrementCount();
        this.setData();

        console.log("data mounted :" + JSON.stringify(this.data));
    }
};
</script>

