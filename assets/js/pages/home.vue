<template>
    <v-app id="inspire">
        <base-layout title="home" active-menu="home">
            <template #content>
                <!-- <data-managment/> -->
            </template>
        </base-layout>
    </v-app>
</template>

<script>
import BaseLayout from '@/pages/layout.vue';


export default {
    name: 'HomeComponent',
    components: {
        BaseLayout,

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

