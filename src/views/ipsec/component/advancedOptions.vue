<template>
  <div class="ml-3 mr-3">
    <h4>Advanced Options</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4" class="mt-0">
        <label>Policy</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="policy" />
        <label class="ml-2">Install policy</label>
      </v-col>
      <v-col cols="4" class="mt-0">
        <label>Rekey</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="rekey" />
        <label class="ml-2">Disable rekey</label>
      </v-col>
      <v-col cols="4" class="mt-0">
        <label>Reauth</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="reauth" />
        <label class="ml-2">Disable reauth</label>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>NAT Traversal</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="NAT Traversal"
          v-model="natTraversal"
          item-title="name"
          item-value="slug"
          return-object
          :items="[
            {
              name: 'Force',
              slug: 'Force',
            },
            { name: 'Unforce', slug: 'Unforce' },
          ]"
        ></v-select>
      </v-col>
      <v-col cols="4">
        <label>MOBIKE</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="mobike" />
        <label class="ml-2">Disable MOBIKE</label>
      </v-col>
      <v-col cols="4">
        <label>Dead Peer Detection</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <input type="checkbox" v-model="deadPeer" />
        <label class="ml-2">Disable dead Peer</label>
        <v-text-field
          class="mt-3"
          label="Seconds"
          v-model="seconds"
        ></v-text-field>
        <v-text-field label="retries" v-model="retries"></v-text-field>
        <v-select
          label="Dead Peer Detection"
          v-model="selectDear"
          item-title="name"
          item-value="slug"
          return-object
          :items="[
            {
              name: 'Default',
              slug: 'default',
            },
            { name: 'Respond only', slug: 'Respond only' },
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
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Inactivity timeout</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          
          label="Inactivity timeout"
          v-model="interactivityTimout"
        ></v-text-field>
        <!-- <v-select
          label="Inactivity timeout"
          v-model="interactivityTimout"
          item-title="name"
          item-value="slug"
          return-object
          :items="[
            {
              name: 'Default',
              slug: 'default',
            },
            { name: 'Respond only', slug: 'Respond only' },
            {
              name: 'Start on traffic',
              slug: 'Start on traffic',
            },
            {
              name: 'Start immediate',
              slug: 'Start immediate',
            },
          ]"
        ></v-select> -->
        <v-text-field
          label="Inactivity timeout"
          v-model="interactivityTimout2"
        ></v-text-field>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Margin time</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="Margin time" v-model="marginTime"></v-text-field>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Rekey fuzz</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="Rekey fuzz" v-model="rekeyFuzz"></v-text-field>
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
  "policy",
  "rekey",
  "reauth",
  "natTraversal",
  "mobike",
  "deadPeer",
  "selectDear",
  "retries",
  "seconds",
  "interactivityTimout",
  "interactivityTimout2",
  "rekeyFuzz",
  "marginTime",
]);
const emit = defineEmits([
  "update:policy",
  "update:rekey",
  "update:reauth",
  "update:natTraversal",
  "update:mobike",
  "update:deadPeer",
  "update:selectDear",
  "update:retries",
  "update:seconds",
  "update:interactivityTimout",
  "update:interactivityTimout2",
  "update:rekeyFuzz",
  "update:marginTime",
]);
const {
  policy,
  rekey,
  reauth,
  natTraversal,
  deadPeer,
  retries,
  mobike,
  selectDear,
  interactivityTimout,
  interactivityTimout2,
  seconds,
  rekeyFuzz,
  marginTime,
} = useVModels(props, emit);
</script>
