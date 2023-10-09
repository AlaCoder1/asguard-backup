<template>
    <v-app id="inspire">
        <base-layout title="home" active-menu="home">
            <template #content>
            </template>
        </base-layout>
    </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';
import GroupManagement from '@/pages/group-management.vue';
import NetworkServerManagement from '@/pages/network-server-management.vue';
import CertificatsManagement from '@/pages/certificats-management.vue';

export default {
    name: 'HomeComponent',
    components: {
        BaseLayout,
        NetworkServerManagement,
        GroupManagement,
        CertificatsManagement,
    },
    computed: {},
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
    },
    beforeMount: async function () {
        this.setData();
    }
};
</script>

