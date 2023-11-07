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
        <label>IPv4 Remote Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="IPv4 Remote Network"></v-text-field>
      </v-col>
      <v-col cols="4" >
        <label>IPv6 Remote Network</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="IPv6 Remote Network"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>Limit outgoing bandwidth</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="Limit outgoing bandwidth"></v-text-field>
      </v-col>
      <v-col cols="4">
        <label>Compression</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select label="Compression"></v-select>
      </v-col>
      <v-col cols="4">
        <label>Type-of-Service</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Infinitely resolve remote server</label>
      </v-col>
      <v-col cols="4">
        <label>IPv6</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Infinitely resolve remote server</label>
      </v-col>
      <v-col cols="4">
        <label> pull routes</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Infinitely resolve remote server</label>
      </v-col>
      <v-col cols="4">
        <label>Add/remove routes</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" />
        <label class="ml-2">Infinitely resolve remote server</label>
      </v-col>
    </v-row>
  </div>
</template>
