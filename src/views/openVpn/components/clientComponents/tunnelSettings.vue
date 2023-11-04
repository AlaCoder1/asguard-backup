<template>
  <div class="ml-3 mr-3">
    <h4>Tunnel Settings</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col align-self="center" cols="4">
        <label>IPv4 Tunnel Network</label>
      </v-col>
      <v-col align-self="center" cols="8" class="mb-n6">
        <v-text-field
          label="IPv4 Tunnel Network"
          v-model="ipv4TunnelNetwork"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.ipv4TunnelNetwork.$errors.length"
        >
          {{ props.errors.ipv4TunnelNetwork.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col align-self="center" cols="4">
        <label>IPv6 Tunnel Network</label>
      </v-col>
      <v-col  align-self="center" cols="8" class="mb-n6">
        <v-text-field
          label="IPv6 Tunnel Network"
          v-model="ipv6TunnelNetwork"
        ></v-text-field>
      </v-col>
      <v-col align-self="center" cols="4">
        <label>IPv4 Remote Network</label>
      </v-col>
      <v-col align-self="center" cols="8" class="mb-n6">
        <v-text-field
          label="IPv4 Remote Network"
          v-model="ipv4RemoteNetwork"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.ipv4RemoteNetwork.$errors.length"
        >
          {{ props.errors.ipv4RemoteNetwork.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col align-self="center"  cols="4">
        <label>IPv6 Remote Network</label>
      </v-col>
      <v-col align-self="center" cols="8" class="mb-n6">
        <v-text-field
          label="IPv6 Remote Network"
          v-model="ipv6RemoteNetwork"
        ></v-text-field>
      </v-col>
      <v-col align-self="center" cols="4">
        <label>Limit outgoing bandwidth</label>
      </v-col>
      <v-col align-self="center" cols="8" class="mb-n6">
        <v-text-field
          label="Limit outgoing bandwidth"
          v-model="limit_outgoing_bandwidth"
        ></v-text-field>
      </v-col>
      <v-col align-self="center" cols="4">
        <label>Compression</label>
      </v-col>
      <v-col align-self="center" cols="8" class="mb-n6">
        <v-select
          label="Compression"
          v-model="compression"
          :items="compressionList"
          item-title="name"
          item-value="slug"
          return-object
        ></v-select>
      </v-col>
      <v-col  cols="4">
        <label>Type-of-Service</label>
      </v-col>
      <v-col  cols="8" class="mb-n6">
        <input type="checkbox" v-model="typeOfService" />
        <label class="ml-2">Infinitely resolve remote server</label>
      </v-col>
      <v-col  cols="4">
        <label>IPv6</label>
      </v-col>
      <v-col  cols="8" class="mb-n6">
        <input type="checkbox" v-model="ipv6" />
        <label class="ml-2">Infinitely resolve remote server</label>
      </v-col>
      <v-col  cols="4">
        <label> pull routes</label>
      </v-col>
      <v-col  cols="8" class="mb-n6">
        <input type="checkbox" v-model="pullRoutes" />
        <label class="ml-2">Infinitely resolve remote server</label>
      </v-col>
      <v-col  cols="4">
        <label>Add/remove routes</label>
      </v-col>
      <v-col  cols="8" class="mb-n6">
        <input type="checkbox" v-model="addRemoveRoutes" />
        <label class="ml-2">Infinitely resolve remote server</label>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import { useVModels } from "@vueuse/core";
import { ref } from "vue";

const compressionList = ref([
  {
    name: "No preference",
    slug: "no_preference",
  },
  {
    name: "Disable-No Compression",
    slug: "disabled",
  },
  {
    name: "Enabled with Adaptive Compression",
    slug: "enabled",
  },
  {
    name: "Enabled without Adaptive Compression",
    slug: "adaptive",
  },
]);
const props = defineProps([
  "errors",
  "ipv4TunnelNetwork",
  "ipv6TunnelNetwork",
  "ipv4RemoteNetwork",
  "ipv6RemoteNetwork",
  "limit_outgoing_bandwidth",
  "compression",
  "typeOfService",
  "ipv6",
  "pullRoutes",
  "addRemoveRoutes",
]);

const emit = defineEmits([
  "update:ipv4TunnelNetwork",
  "update:ipv6TunnelNetwork",
  "update:ipv4RemoteNetwork",
  "update:ipv6RemoteNetwork",
  "update:limit_outgoing_bandwidth",
  "update:compression",
  "update:typeOfService",
  "update:ipv6",
  "update:pullRoutes",
  "update:addRemoveRoutes",
]);

const {
  ipv4TunnelNetwork,
  ipv6TunnelNetwork,
  ipv4RemoteNetwork,
  ipv6RemoteNetwork,
  limit_outgoing_bandwidth,
  compression,
  typeOfService,
  ipv6,
  pullRoutes,
  addRemoveRoutes,
} = useVModels(props, emit);
</script>
