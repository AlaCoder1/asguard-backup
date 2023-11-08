<template>
  <v-container class="mt-5 mb-5">
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="primary">
            <span>IPv4 Address</span>
          </v-card-title>
          <v-card-text>
            <v-form>
              <v-typography class="title-text ml-3">{{
                ipAddress
              }}</v-typography>
              <v-text-field
                variant="outlined"
                label="IPv4 Address Alias"
                v-model="interfaceDHCPAdvanced.ipv4_address"
              ></v-text-field>

              <v-select
                variant="outlined"
                v-model="interfaceDHCPAdvanced.ipv4_netmask"
                :items="netmasks"
                label="Netmask"
              ></v-select>

              <v-text-field
                variant="outlined"
                label="Reject leases from"
                v-model="interfaceDHCPAdvanced.rejectLeases"
              ></v-text-field>

              <v-text-field
                variant="outlined"
                label="Hostname"
                v-model="interfaceDHCPAdvanced.hostname"
              ></v-text-field>

              <v-checkbox
                v-model="interfaceDHCPAdvanced.overrideMTU"
                label="Override MTU"
              ></v-checkbox>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: "ConfigDHCPv4",
  props: {
    interfaceDHCPAdvanced: {
      type: Object,
      required: true,
    },
    ipAddress: {
      type: String,
    },
  },
  data() {
    return {
      netmasks: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    };
  },
};
</script>
