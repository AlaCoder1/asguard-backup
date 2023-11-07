<template>
  <div class="ml-3 mr-3">
    <h4>Tunnel Settings</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4">
        <label>IPv4 Tunnel Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="IPv4 Tunnel Network"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>IPv6 Tunnel Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="IPv6 Tunnel Network"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>Gateway</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">redirect Gateway</label>
      </v-col>

      <v-col cols="4">
        <label>Bridge</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">DHCP bridge</label>
      </v-col>

      <v-col cols="4">
        <label>Interface bridge</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select label="Interface bridge"></v-select>
      </v-col>

      <v-col cols="4">
        <label>Start DHCP bridge</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="Start DHCP bridge"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>End DHCP bridge</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="End DHCP bridge"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>IPv4 Local Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="IPv4 Local Network"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>IPv6 Local Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="IPv6 Local Network"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>IPv4 Remote Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="IPv4 Remote Network"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>IPv6 Remote Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="IPv6 Remote Network"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>Concurrent connections</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="Concurrent connections"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>Compression</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select label="Compression"></v-select>
      </v-col>

      <v-col cols="4">
        <label>Type of service</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Active type of service</label>
      </v-col>
      <v-col cols="4">
        <label>Connections</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Duplicate connections</label>
      </v-col>
      <v-col cols="4">
        <label>IPv6</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Disable IPv6</label>
      </v-col>
      <v-col cols="4">
        <label>Inter clients</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Communication inter clients</label>
      </v-col>
    </v-row>
  </div>
</template>
