<template>
    <div class="ml-3 mt-3 mr-3">
        <table class="ml-3 mt-3 mr-5">
            <tbody>
                <tr style="width: 100%;">
                    <!-- <v-text-field label="IP Adress " class="ml-3 mt-1" disabled v-model="ipAddress"></v-text-field> -->
                    <v-text-field label="IP Adress " class="ml-3 mt-1" disabled></v-text-field>

                </tr>
                <tr>
                    <td><span style="color: black;" class="">IPv4 Adress Alias</span></td>
                    <td>
                        <div style="display: flex">
                            <ValidationProvider name="IPv4AdressAlias"
                                :rules="{ regex: /^(?:(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$/ }"
                                v-slot="{ errors }">
                                <v-text-field label="Enter IP Adress Alias" class="ml-3 mt-1"
                                    v-model="interfaceDHCPAdvanced.ipv4_adress" :error-messages="errors"></v-text-field>
                            </ValidationProvider>
                            <ValidationProvider name="netmask4" :rules="netmaskValidationRule" v-slot="{ errors }">
                                <v-select v-model="interfaceDHCPAdvanced.ipv4_netmask" :items="netmasks"
                                    :error-messages="errors" label="Netmask" class="ml-3 mr-3"></v-select>
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
                                v-model="interfaceDHCPAdvanced.rejectLeases" :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Hostname</span></td>
                    <td>
                        <ValidationProvider name="hostname"
                            :rules="{ regex: /^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$/ }"
                            v-slot="{ errors }">
                            <v-text-field label="Enter Hostname" class="ml-3 mt-1" v-model="interfaceDHCPAdvanced.hostname"
                                :error-messages="errors"></v-text-field>
                        </ValidationProvider>

                    </td>
                </tr>
                <!-- todo not yet developped -->
                <!-- <tr>
                    <td><span style="color: black;" class="">Override MTU</span></td>
                    <td>
                        <ValidationProvider name="overrideMTU" rules="required" v-slot="{ errors }">
                            <input type="checkbox" v-model="interfaceDHCPAdvanced.overrideMTU" class="ml-3 mr-3" />
                            <label>MTU</label>
                        </ValidationProvider>
                    </td>
                </tr> -->
            </tbody>
        </table>
        <v-card-title class="title-text">Protocol Timing</v-card-title>
        <v-divider class="ml-3"></v-divider>
        <table class="ml-3 mt-3 mr-5">
            <tbody>
                <tr>
                    <td><span style="color: black;" class="">Timeout</span></td>
                    <td>
                        <!-- must be number  -->
                        <ValidationProvider name="timeout" rules="numeric" v-slot="{ errors }">
                            <v-text-field label="Enter Timeout" class="ml-3 mt-1" v-model="interfaceDHCPAdvanced.timeout"
                                :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Try again</span></td>
                    <td style="width: 80%;">
                        <ValidationProvider name="tryAgain" rules="numeric" v-slot="{ errors }">
                            <v-text-field label="Enter Try again" class="ml-3 mt-1" v-model="interfaceDHCPAdvanced.retry"
                                :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black; width: 50%;" class="">Select expiration</span></td>
                    <td style="width: 50%;">
                        <ValidationProvider name="selectExpiration" rules="numeric" v-slot="{ errors }">
                            <v-text-field label="Enter Select expiration" class="ml-3 mt-1"
                                v-model="interfaceDHCPAdvanced.select_timeout" :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Restart</span></td>
                    <td style="width: 80%;">
                        <ValidationProvider name="restart" rules="numeric" v-slot="{ errors }">
                            <v-text-field label="Enter Restart" class="ml-3 mt-1" v-model="interfaceDHCPAdvanced.reboot"
                                :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Backoff Cutoff</span></td>
                    <td style="width: 80%;">
                        <ValidationProvider name="backoffCutoff" rules="numeric" v-slot="{ errors }">
                            <v-text-field label="Enter Backoff Cutoff" class="ml-3 mt-1"
                                v-model="interfaceDHCPAdvanced.backoff" :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Initial Interval</span></td>
                    <td style="width: 80%;">
                        <ValidationProvider name="initialInterval" rules="numeric" v-slot="{ errors }">
                            <v-text-field label="Enter Initial Interval" class="ml-3 mt-1"
                                v-model="interfaceDHCPAdvanced.initial_interval" :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
            </tbody>
        </table>
        <v-card-title class="title-text">Lease Requirements</v-card-title>
        <v-divider class="ml-3"></v-divider>
        <table class="ml-3 mt-3 mr-5">
            <tbody>
                <tr>
                    <td><span style="color: black;" class="">Send options DHCP Client</span></td>
                    <td style="width: 70%;">
                        <ValidationProvider name="sendOptionsDHCPClient"
                            :rules="{ regex: /^[a-zA-Z0-9]+(?:,[a-zA-Z0-9]+)*$/ }" v-slot="{ errors }">
                            <v-text-field class="ml-3 mt-1" label="Enter Send options DHCP Client"
                                v-model="interfaceDHCPAdvanced.dhcp_client"
                                :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Send Options lease time</span></td>
                    <td style="width: 70%;">
                        <ValidationProvider name="sendOptionsLeaseTime" rules="numeric" v-slot="{ errors }">
                            <v-text-field class="ml-3 mt-1" label="Enter Send Options lease time"
                                v-model="interfaceDHCPAdvanced.lease_time"
                                :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Request Options</span></td>
                    <td style="width: 70%;">
                        <ValidationProvider name="requestOptions" :rules="{ regex: /^[a-zA-Z0-9]*$/ }" v-slot="{ errors }">
                            <v-text-field class="ml-3 mt-1" label="Enter Request Options"
                                v-model="interfaceDHCPAdvanced.request" :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Required Options</span></td>
                    <td style="width: 70%;">
                        <ValidationProvider name="requiredOptions" :rules="{ regex: /^[a-zA-Z0-9]*$/ }" v-slot="{ errors }">
                            <v-text-field class="ml-3 mt-1" label="Enter Required Options"
                                v-model="interfaceDHCPAdvanced.require" :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Supersede domaine name</span></td>
                    <td style="width: 70%;">
                        <ValidationProvider name="supersedeDomaineName"
                            :rules="{ regex: /^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$/ }"
                            v-slot="{ errors }">
                            <v-text-field class="ml-3 mt-1" label="Enter Supersede domaine name"
                                v-model="interfaceDHCPAdvanced.domain_name"
                                :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
                <tr>
                    <td><span style="color: black;" class="">Prepend domain server</span></td>
                    <td style="width: 70%;">
                        <ValidationProvider name="prependDomainServer"
                            :rules="{ regex: /^(http|https):\/\/[a-zA-Z0-9]+(?:,[a-zA-Z0-9]+)*$/ }" v-slot="{ errors }">
                            <v-text-field class="ml-3 mt-1" label="Enter Prepend domain server"
                                v-model="interfaceDHCPAdvanced.domain_server"
                                :error-messages="errors"></v-text-field>
                        </ValidationProvider>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script>
export default {
    name: "AdvancedConfigDHCPv4",
    props: {
        interfaceDHCPAdvanced: {
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
        'interfaceDHCPAdvanced.ipv4_address': function (newVal) {
            this.ipAddressValid = /^(?:(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$/.test(newVal);
        },
    },

};

</script>

<style scoped>
.title-text {
    color: #020202;
    font-family: Nunito;
    font-size: 18px;
    font-style: normal;
    font-weight: 700;
    line-height: normal;
}
</style>