<template>
  <div class="mt-3">
    <h4 class="mt-6">Client Settings</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4">
        <label>Dynamic IP</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Active Dynamic IP</label>
      </v-col>
      <v-col cols="4">
        <label>Adress Pool</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Active Adress pool</label>
        <v-text-field class="mt-3 mb-n6" label="text"></v-text-field>
        <v-text-field class="mt-3" label="text"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>Topology</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Active toplogy</label>
      </v-col>
      <v-col cols="4">
        <label>DNS Default Domain</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Active DNS Default Domain </label>
        <v-text-field class="mt-3" label="text"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>DNS Servers</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Active DNS Servers </label>
        <v-text-field class="mt-3 mb-n6" label="text"></v-text-field>
        <v-text-field class="mt-3" label="text"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>Force DNS cache update</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Active Force DNS cahce update </label>
      </v-col>
      <v-col cols="4">
        <label>NTP Servers</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Active NTP Servers</label>
        <v-text-field class="mt-3 mb-n6" label="text"></v-text-field>
        <v-text-field class="mt-3" label="text"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>Client Management Port</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Active Client Management Port</label>
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  data() {
    return {};
  },
};
</script>
