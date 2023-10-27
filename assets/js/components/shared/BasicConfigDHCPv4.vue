<template>
    <v-app class="ml-3 mt-3 mr-3">
        <table class="ml-3 mt-3 mr-5">
            <tbody>
                <tr style="width: 100%;">
                    <v-text-field label="IP Adress " class="ml-3 mt-1" disabled v-model="ipAddress"></v-text-field>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">IPv4 Adress Alias</span></td>
                    <td>
                        <div style="display: flex">
                            <ValidationProvider name="IPv4AdressAlias"
                                :rules="{ regex: /^(?:(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$/ }"
                                v-slot="{ errors }">
                                <v-text-field label="Enter IP Adress Alias" class="ml-3 mt-1"
                                    v-model="interface.ipv4_adress" :error-messages="errors"></v-text-field>
                            </ValidationProvider>
                            <ValidationProvider name="netmask4" :rules="netmaskValidationRule" v-slot="{ errors }">
                                <v-select v-model="interface.ipv4_netmask" :items="netmasks" :error-messages="errors"
                                    label="Netmask" class="ml-3 mr-3"></v-select>
                            </ValidationProvider>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Reject leases from</span></td>
                    <td>
                        <ValidationProvider name="rejectLeases"
                            :rules="{ regex: /^(?:(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$/ }"
                            v-slot="{ errors }">
                            <v-text-field label="Enter Reject leases from" class="ml-3 mt-1"
                                v-model="interface.rejectLeases" :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Hostname</span></td>
                    <td>
                        <ValidationProvider name="hostname"
                            :rules="{ regex: /^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$/ }"
                            v-slot="{ errors }">
                            <v-text-field label="Enter Hostname" class="ml-3 mt-1" v-model="interface.hostname"
                                :error-messages="errors"></v-text-field>
                        </ValidationProvider>

                    </td>
                </tr>
                <!-- todo not yet developped -->
                <!-- <tr>
                    <td><span style="color: black;" class="">Override MTU</span></td>
                    <td>
                        <ValidationProvider name="overrideMTU" rules="required" v-slot="{ errors }">
                            <input type="checkbox" v-model="interface.overrideMTU" class="ml-3 mr-3" />
                            <label>MTU</label>
                        </ValidationProvider>
                    </td>
                </tr> -->
            </tbody>
        </table>
    </v-app>
</template>
<script>
export default {
    name: "BasicConfigDHCPv4",
    props: {
        interface: {
            type: Object,
            required: true
        },
        ipAddress: {
            type: String,
        },
    },
    data() {
        return {
            netmasks: [
                "32",
                "31",
                "30",
                "29",
                "28",
                "27",
                "26",
                "25",
                "24",
                "23",
                "22",
                "21",
                "20"
            ],
            ipAddressValid: false,
        };
    },
    beforeMount() {
    },
    computed: {
        netmaskValidationRule() {
            return this.ipAddressValid ? 'required' : '';
        },
    },
    watch: {
        'interface.ipv4_address': function (newVal) {
            this.ipAddressValid = /^(?:(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$/.test(newVal);
        },
    },

};

</script>

<style scoped></style>