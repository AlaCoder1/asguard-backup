<template>
    <v-app class="ml-3 mt-3">
        <div>
            <label class="mt-8">IPv4 Adress Alias</label>
            <v-text-field v-model="lan.ipv4_address" label="IPv4 Address" class="ml-3"></v-text-field>
            <v-select v-model="lan.ipv4_netmask" :items="netmasks" label="Netmask" class="ml-3 mr-3"></v-select>
        </div>
        <div>
             <label class="mt-8">Reject leases from</label>
                <v-text-field v-model="lan.rejectLeases" label="IPv4 Address" class="ml-3"></v-text-field>
        </div>
        <div>
             <label class="mt-8">Hostname</label>
                <v-text-field v-model="lan.hostname" label="IPv4 Address" class="ml-3"></v-text-field>
        </div>
        <div>
             <label class="mt-8">Override MTU</label>
             <input type="checkbox" v-model="lan.overrideMTU" class="ml-3" />
             <label class="mt-8">MTU</label>
        </div>
    </v-app>
</template>
<script>
export default {
    data() {
        return {
            netmasks: [
                " /32",
                " /31",
                " /30",
                " /29",
                " /28",
                " /27",
                " /26",
                " /25",
                " /24",
                " /23",
                " /22",
                " /21",
                " /20"
            ],
            lan: {
                ipv4_address: "",
                ipv4_netmask: "",
                rejectLeases: "",
                hostname: "",
                overrideMTU: false,
                mtu: ""
            }
        };
    },
    beforeMount() {
        this.lan = this.$root.$data.lan;
    },
};

</script>

<style scoped></style>