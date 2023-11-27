<template>
  <div class="ml-3 mr-3">
    <h4>General information phase1</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4" class="mt-5">
        <label>Tunnel settings name</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Tunnel settings name"
          v-model="tunnelSettings"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.tunnelSettings.$errors.length"
        >
          {{ props.errors.tunnelSettings.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Connection method</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Connection method"
          v-model="connectionMethod"
          item-title="name"
          item-value="slug"
          return-object
          :items="[
            {
              name: 'Default',
              slug: 'default',
            },
            { name: 'Respond only', slug: 'Respond Only' },
            {
              name: 'Start on traffic',
              slug: 'Start on traffic',
            },
            {
              name: 'Start immediate',
              slug: 'Start immediate',
            },
          ]"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.connectionMethod.$errors.length"
        >
          {{ props.errors.connectionMethod.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Key Exchange version</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Key Exchange version"
          v-model="keyExchange"
          item-title="name"
          item-value="slug"
          return-object
          :items="[
            {
              name: 'auto',
              slug: 'auto',
            },
            { name: 'V1', slug: 'v1' },
            {
              name: 'V2',
              slug: 'v2',
            },
          ]"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.keyExchange.$errors.length"
        >
          {{ props.errors.keyExchange.$errors?.[0].$message }}
        </p>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Internet Protocol</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Internet Protocol"
          v-model="internetProtocol"
          item-title="name"
          item-value="slug"
          return-object
          :items="[
            {
              name: 'IPv4',
              slug: 'IPv4',
            },
            { name: 'IPv6', slug: 'IPv6' },
          ]"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.internetProtocol.$errors.length"
        >
          {{ props.errors.internetProtocol.$errors?.[0].$message }}
        </p>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Interface</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          v-model="generalinterface"
          label="Interface"
          item-title="name"
          item-value="id"
          return-object
          :items="props.mapedInterface"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.generalinterface.$errors.length"
        >
          {{ props.errors.generalinterface.$errors?.[0].$message }}
        </p>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Remote gateway</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Remote gateway"
          v-model="remoteGateway"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.remoteGateway.$errors.length"
        >
          {{ props.errors.remoteGateway.$errors?.[0].$message }}
        </p>
      </v-col>

      <v-col cols="4" class="mt-0">
        <label>Dynamic gateway</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="remoteConnect" />
        <label class="ml-2"> Allow any remote gateway to connect</label>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Description</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="Description" v-model="description"></v-text-field>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import { useVModels } from "@vueuse/core";

const props = defineProps([
  "errors",
  "mapedInterface",
  "tunnelSettings",
  "connectionMethod",
  "keyExchange",
  "internetProtocol",
  "remoteGateway",
  "generalinterface",
  "remoteConnect",
  "description",
]);
const emit = defineEmits([
  "update:tunnelSettings",
  "update:connectionMethod",
  "update:keyExchange",
  "update:internetProtocol",
  "update:remoteGateway",
  "update:generalinterface",
  "update:remoteConnect",
  "update:description",
]);
const {
  tunnelSettings,
  connectionMethod,
  keyExchange,
  internetProtocol,
  generalinterface,
  description,
  remoteGateway,
  remoteConnect,
} = useVModels(props, emit);
</script>
