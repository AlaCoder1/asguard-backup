<template>
  <div class="ml-3 mr-3 mt-5">
    <h4>Phase 1 proposal (Authentication)</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4" class="mt-5">
        <label>Authentication method</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Authentication method"
          v-model="authMethod"
          item-title="name"
          item-value="slug"
          return-object
          :items="[
            {
              name: 'Mutual PSK',
              slug: 'Mutual PSK',
            },
            { name: 'Mutual Public key', slug: 'Mutual Public key' },
            {
              name: 'Mutual RSA',
              slug: 'Mutual RSA',
            },
          ]"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.authMethod.$errors.length"
        >
          {{ props.errors.authMethod.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Negotiation mode</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Negotiation mode"
          v-model="negotiationMode"
          item-title="name"
          item-value="slug"
          return-object
          :items="[
            {
              name: 'Main',
              slug: 'Main',
            },
            { name: 'Aggressive', slug: 'Aggressive' },
          ]"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.negotiationMode.$errors.length"
        >
          {{ props.errors.negotiationMode.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" class="mt-6">
        <label>Pre-Shared Key</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-textarea
        rows="1"
          row-height="15"
          class="mt-3"
          v-model="sharedKey"
          label="Pre-Shared Key"
          variant="outlined"
        ></v-textarea>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.sharedKey.$errors.length"
        >
          {{ props.errors.sharedKey.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>My Certificate</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          v-model="certificate"
          label="My Certificate"
          item-title="name"
          item-value="id"
          return-object
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.certificate.$errors.length"
        >
          {{ props.errors.certificate.$errors?.[0].$message }}
        </p>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label
          >Peer identifier <br />
          ex CN= ,C= ,O=</label
        >
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Peer identifier"
          v-model="peerIdentifier"
        ></v-text-field>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Local Key Pair</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          v-model="localKey"
          label="Local Key Pair"
          item-title="name"
          item-value="id"
          return-object
        ></v-select>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Peer Key Pair</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          v-model="keyPair"
          label="Peer Key Pair"
          item-title="name"
          item-value="id"
          return-object
        ></v-select>
      </v-col>
    </v-row>
    <v-row class="mt-2">
      <div class="ml-3 mr-3">
        <v-row class="mt-2"> </v-row>
      </div>
    </v-row>
    <v-spacer></v-spacer>
  </div>
</template>
<script setup>
import { useVModels } from "@vueuse/core";

const props = defineProps([
  "errors",
  "authMethod",
  "negotiationMode",
  "sharedKey",
  "localKey",
  "certificate",
  "peerIdentifier",
  "keyPair",
]);
const emit = defineEmits([
  "update:authMethod",
  "update:negotiationMode",
  "update:sharedKey",
  "update:localKey",
  "update:certificate",
  "update:keyPair",
  "update:peerIdentifier",
]);
const {
  authMethod,
  negotiationMode,
  sharedKey,
  certificate,
  keyPair,
  localKey,
  peerIdentifier,
} = useVModels(props, emit);
</script>
