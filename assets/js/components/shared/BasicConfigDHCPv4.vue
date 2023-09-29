<template>
    <v-app class="ml-3 mt-3 mr-3">
        <div style="display: flex; align-items: center; margin-top: 8px;">
            <label style="width: 150px;">IPv4 Adress Alias</label>
            <v-text-field v-model="interface.ipv4_adress" class="ml-3"></v-text-field>
            <v-select v-model="interface.ipv4_netmask" :items="netmasks" label="Netmask" class="ml-3 mr-3"></v-select>
        </div>

        <div style="display: flex; align-items: center; margin-top: 8px;">
            <label style="width: 150px;">Reject leases from</label>
            <v-text-field v-model="interface.rejectLeases" class="ml-3  mr-3"></v-text-field>
        </div>

        <div style="display: flex; align-items: center; margin-top: 8px;">
            <label style="width: 150px;">Hostname</label>
            <v-text-field v-model="interface.hostname" class="ml-3 mr-3"></v-text-field>
        </div>

        <div style="display: flex; align-items: center; margin-top: 8px;">
            <label style="width: 150px;">Override MTU</label>
            <input type="checkbox" v-model="interface.overrideMTU" class="ml-3 mr-3" />
            <label>MTU</label>
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
            interface: {
                ipv4_adress: "",
                ipv4_netmask: "",
                rejectLeases: "",
                hostname: "",
                overrideMTU: false,
                mtu: ""
            }
        };
    },
    beforeMount() {
    },
};

</script>

<style scoped></style>