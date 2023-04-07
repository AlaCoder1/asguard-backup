<template>
<div>
da

</div>
  
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
