<template>
    <p> heni </p>
</template>

<script>


export default {
    name: 'HomeComponent',
    data() {
        return {
        tab,
        };
    },
    mounted: async function () {
            this.tab= this.$root.$data.tab ;
            console.log("out data from django",this.tab);
        }
};
</script>
