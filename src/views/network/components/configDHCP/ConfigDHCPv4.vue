<template>
  <div class="mt-5 mb-5">
    <v-row>
      <v-col cols="12">
        <div class="mr-2 ml-2">
          <v-row class="mt-2">
            <v-col cols="12">
              <v-text-field
                :model-value="ipAddress"
                label="IPV4 address"
                variant="outlined"
                readonly
              ></v-text-field>
            </v-col>
            <v-col align-self="center" cols="4">
              <label class="ml-2">IPV4 address</label>
              <small style="color: red">*</small>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field
                label="Enter IPV4 address"
                v-model="ipv4_address"
                class="ip-address-style"
              ></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-select
                v-model="ipv4_netmask"
                :items="netmasks"
                class="ml-3 netmask-select-style"
              ></v-select>
            </v-col>
            <v-col align-self="center" cols="4">
              <label class="ml-2">Reject leases from</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Reject leases from"
                v-model="rejectLeases"
              ></v-text-field>
            </v-col>
            <v-col align-self="center" cols="4">
              <label class="ml-2">Hostname</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                label="Hostname"
                v-model="hostname"
              ></v-text-field>
            </v-col>
            <v-col align-self="center" cols="4">
              <label class="ml-2">Override MTU</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-checkbox
                v-model="overrideMTU"
                label="Override MTU"
              ></v-checkbox>
            </v-col>
          </v-row>
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { useVModels } from "@vueuse/core";
import { ref } from "vue";
import netmaskItems from "../../../../constants/netmask.js";

const netmasks = ref(netmaskItems);

const props = defineProps([
  "errors",
  "ipAddress",
  "ipv4_address",
  "ipv4_netmask",
  "rejectLeases",
  "hostname",
  "overrideMTU",
]);

const emit = defineEmits([
  "update:ipv4_netmask",
  "update:ipv4_address",
  "update:rejectLeases",
  "update:hostname",
  "update:overrideMTU"
]);

const {
  ipv4_netmask,
  ipv4_address,
  rejectLeases,
  hostname,
  overrideMTU
} = useVModels(props, emit);

</script>
