<template>
  <div class="mt-3">
    <h4 class="mt-6">Client Settings</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4" align-self="center">
        <label>Dynamic IP</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="dynamicIP" />
        <label class="ml-2">Active Dynamic IP</label>
      </v-col>
      <v-col cols="4" >
        <label>Adress Pool</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="adressPool" />
        <label class="ml-2">Active Adress pool</label>
        <v-text-field
          class="mt-3 mb-n6"
          label="Start"
          v-model="startAddressPool"
          v-if="adressPool"
        ></v-text-field>
        <p
          class="error-feedback mb-5 mt-3"
          v-if="props.errors.startAddressPool.$errors.length"
        >
          {{ props.errors.startAddressPool.$errors?.[0].$message }}
        </p>
        <v-text-field
          class="mt-3"
          label="End"
          v-model="endAddressPool"
          v-if="adressPool"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.endAddressPool.$errors.length"
        >
          {{ props.errors.endAddressPool.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>Topology</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="topology" />
        <label class="ml-2">Active toplogy</label>
      </v-col>
      <v-col cols="4">
        <label>DNS Default Domain</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="dnsDefaultDomain" />
        <label class="ml-2">Active DNS Default Domain </label>
        <v-text-field
          class="mt-3"
          v-model="activeDnsDefault"
          label="DNS Default Domain"
          v-if="dnsDefaultDomain"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.activeDnsDefault.$errors.length"
        >
          {{ props.errors.activeDnsDefault.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4">
        <label>DNS Servers</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="dnsServers" />
        <label class="ml-2">Active DNS Servers </label>
        <v-text-field
          class="mt-3 mb-n6"
          v-model="activeDnsServer1"
          label="DNS Servers 1"
          v-if="dnsServers"
        ></v-text-field>
        <p
          class="error-feedback mb-5 mt-3"
          v-if="props.errors.activeDnsServer1.$errors.length"
        >
          {{ props.errors.activeDnsServer1.$errors?.[0].$message }}
        </p>
        <v-text-field
          class="mt-3"
          label="DNS Servers 2"
          v-model="activeDnsServer2"
          v-if="dnsServers"
        ></v-text-field>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>Force DNS cache update</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="forceDNS" />
        <label class="ml-2">Active Force DNS cahce update </label>
      </v-col>
      <v-col cols="4">
        <label>NTP Servers</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="ntpServers" />
        <label class="ml-2">Active NTP Servers</label>
        <v-text-field
          class="mt-3 mb-n6"
          label="NTP Servers 1"
          v-model="activeNtpServer1"
          v-if="ntpServers"
        ></v-text-field>
        <p
          class="error-feedback mb-5 mt-3"
          v-if="props.errors.activeNtpServer1.$errors.length"
        >
          {{ props.errors.activeNtpServer1.$errors?.[0].$message }}
        </p>
        <v-text-field
          class="mt-3"
          label="NTP Servers 2"
          v-model="activeNtpServer2"
          v-if="ntpServers"
        ></v-text-field>
      </v-col>
      <v-col cols="4" align-self="center">
        <label>Client Management Port</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="clientPort" />
        <label class="ml-2">Active Client Management Port</label>
      </v-col>
      <v-col align-self="center" cols="4" class="mb-5">
        <label>Verbosity Level</label>
      </v-col>
      <v-col cols="8">
        <v-select
          label="Verbosity Level"
          v-model="verbLevel"
          :items="verbosityLevelList"
          item-title="name"
          item-value="slug"
          return-object
        ></v-select>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useVModels } from "@vueuse/core";

const props = defineProps([
  "errors",
  "dynamicIP",
  "adressPool",
  "topology",
  "dnsDefaultDomain",
  "dnsServers",
  "forceDNS",
  "ntpServers",
  "clientPort",
  "startAddressPool",
  "endAddressPool",
  "activeDnsDefault",
  "activeDnsServer1",
  "activeDnsServer2",
  "activeNtpServer1",
  "activeNtpServer2",
  "verbLevel",
]);
const emit = defineEmits([
  "update:adressPool",
  "update:verbLevel",
  "update:topology",
  "update:dnsDefaultDomain",
  "update:dnsServers",
  "update:forceDNS",
  "update:ntpServers",
  "update:clientPort",
  "update:endAddressPool",
  "update:startAddressPool",
  "update:activeDnsDefault",
  "update:activeDnsServer1",
  "update:activeDnsServer2",
  "update:activeNtpServer1",
  "update:activeNtpServer2",
  "update:dynamicIP",
]);
const {
  verbLevel,
  adressPool,
  topology,
  dnsDefaultDomain,
  forceDNS,
  endAddressPool,
  dnsServers,
  ntpServers,
  activeDnsServer1,
  activeDnsServer2,
  activeNtpServer1,
  activeNtpServer2,
  clientPort,
  dynamicIP,
  activeDnsDefault,
  startAddressPool,
} = useVModels(props, emit);
const verbosityLevelList = ref([
  {
    name: "0 (none)",
    slug: "0",
  },
  {
    name: "1 (default)",
    slug: "1",
  },
  {
    name: "2",
    slug: "2",
  },
  {
    name: "3",
    slug: "3",
  },
  {
    name: "4",
    slug: "4",
  },
  {
    name: "5",
    slug: "5",
  },
  {
    name: "6",
    slug: "6",
  },
  {
    name: "7",
    slug: "7",
  },
  {
    name: "8",
    slug: "8",
  },
  {
    name: "9",
    slug: "9",
  },
  {
    name: "10",
    slug: "10",
  },
  {
    name: "11",
    slug: "11",
  },
]);
</script>
