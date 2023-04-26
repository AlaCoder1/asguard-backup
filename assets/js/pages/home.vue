<template>
    <v-app id="inspire">
        <base-layout
            title="test"
            active-menu="home"
        >
        <template #content>
            <!-- content -->
            <v-container
                class="ma-4 axe-media-print-hide"
                fluid
            />
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
