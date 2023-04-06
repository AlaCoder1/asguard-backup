<template>
<div>

 <ul>
 
  
  </ul>
</div>
  
</template>

<script>


export default {
    name: 'HomeComponent',
    data() {
        return {
            users:'',
        };
    },
    beforeMount: async function () {
        this.users= this.$root.$data.tab ;

        console.log("out data from django",this.users);
        
    }
};
</script>
