<template>
    <div>
        <v-row class="ml-3 mt-9">
            <div style="color: black;" class="ml-3">Use IPV4 connectivity</div>
            <input type="checkbox" class="ml-5" v-model="useIPV4Connectivity">
            <div style="color: black;" class="ml-3">IPV4 Connectivity</div>
        </v-row>
        <v-row class="ml-3 mt-5">
            <div style="color: black;" class="ml-3 inline-input mt-5">Use VLAN Priority</div>
            <v-select class="ml-3 inline-input" style="margin-top: -10px !important;" v-model="useVLANPriority"></v-select>
        </v-row>
        <br />
    </div>
</template>
<script>
export default {
    data() {
        return {
            useIPV4Connectivity: false,
            useVLANPriority: "",

        };
    },
};

</script>

<style scoped>
.inline-input {
    display: inline-block;
    vertical-align: middle;
}
</style>