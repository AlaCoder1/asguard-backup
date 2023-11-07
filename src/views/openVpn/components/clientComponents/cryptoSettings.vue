<template>

    <h4>Cryptographic Settings</h4>
    <v-divider class="mt-2"></v-divider>
    <v-col cols="4">
      <label>Retry DNS resolution</label>
    </v-col>
    <v-col cols="8" class="mb-n6">
      <input type="checkbox" />
      <label class="ml-2">Automatically generate a shared TLS authentication key</label>
      <!-- <label>Enable authentication of TLS packets</label> -->
      <br />
      <!-- <input type="checkbox" />
      <label class="ml-2">Automatically generate a shared TLS authentication key</label> -->
      <br />
    </v-col>
    <v-col cols="4">
      <label>Shared key</label>
    </v-col>
    <v-col cols="8" class="mb-n6">
      <input type="checkbox" />
      <label class="ml-2">Automatically generate a shared key.</label>
      <v-text-field class="mt-3" label="Shared key"></v-text-field>
    </v-col>
    <v-col cols="4">
      <label>Peer Certificate Authority</label>
    </v-col>
    <v-col cols="8" class="mb-n6">
      <v-select label="Peer Certificate Authority"></v-select>
    </v-col>
    <v-col cols="4">
      <label>Client Certificate</label>
    </v-col>
    <v-col cols="8" class="mb-n6">
      <v-select label="Client Certificate"></v-select>
    </v-col>
    <v-col cols="4">
      <label>Encryption algorithm</label>
    </v-col>
    <v-col cols="8" class="mb-n6">
      <v-select label="Encryption algorithm"></v-select>
    </v-col>
    <v-col cols="4">
      <label>Auth Digest Algorithm</label>
    </v-col>
    <v-col cols="8" class="mb-n6">
      <v-select label="Auth Digest Algorithm"></v-select>
    </v-col>
    <v-col cols="4">
      <label>Hardware Crypto</label>
    </v-col>
    <v-col cols="8" class="mb-n6">
      <v-select label="Hardware Crypto"></v-select>
    </v-col>

</template>
