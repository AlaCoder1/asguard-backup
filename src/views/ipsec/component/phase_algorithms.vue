<template>
  <div class="ml-3 mr-3 mt-5">
    <h4>Phase 1 proposal (Algorithms)</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4" class="mt-5">
        <label>Encryption algorithm</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Encryption algorithm"
          v-model="encryptAlgo"
          item-title="name"
          item-value="slug"
          return-object
          :items="[
            {
              name: '128 bit AES-GCM with 128 bit ICV',
              slug: '128',
            },
            {
              name: '192 bit AES-GCM with 128 bit ICV',
              slug: '192',
            },
            {
              name: '256 bit AES-GCM with 128 bit ICV',
              slug: '256',
            },
          ]"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.encryptAlgo.$errors.length"
        >
          {{ props.errors.encryptAlgo.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Hash algorithm</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Hash algorithm"
          v-model="hashAlgo"
          multiple
          item-title="name"
          item-value="slug"
          return-object
          :items="[
            {
              name: 'SHA256',
              slug: 'sha256',
            },
            { name: 'SHA384', slug: 'sha384' },
            {
              name: 'SHA512',
              slug: 'sha512',
            },
          ]"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.hashAlgo.$errors.length"
        >
          {{ props.errors.hashAlgo.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>DH key group</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="DH key group"
          v-model="dhKey"
          multiple
          item-title="name"
          item-value="slug"
          return-object
          :items="dhKeyList"
        ></v-select>
        <p class="error-feedback mb-5" v-if="props.errors.dhKey.$errors.length">
          {{ props.errors.dhKey.$errors?.[0].$message }}
        </p>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Lifetime (unité)</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="Lifetime" v-model="lifetime"></v-text-field>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import { ref } from "vue";
import { useVModels } from "@vueuse/core";
const dhKeyList = ref([
  {
    name: "15 (3072 bits)",
    slug: "15:3072",
  },
  { name: "16 (4096 bits)", slug: "16:4096" },
  {
    name: "17 (6144 bits)",
    slug: "17:6144",
  },
  {
    name: "18 (8192 bits)",
    slug: "18:8192",
  },
  {
    name: "19 (NIST EC 256 bits)",
    slug: "19:256",
  },
  {
    name: "20 (NIST EC 384 bits)",
    slug: "20:384",
  },
  {
    name: "21 (NIST EC 521 bits)",
    slug: "21:521",
  },
  {
    name: "28 (Brainpool EC 256 bits)",
    slug: "28:256",
  },
  {
    name: "29 (Brainpool EC 384 bits)",
    slug: "29:384",
  },
  {
    name: "30 (Brainpool EC 512 bits)",
    slug: "30:512",
  },
  {
    name: "31 (Elliptic Curve 25519)",
    slug: "31:25519",
  },
]);

const props = defineProps([
  "errors",
  "encryptAlgo",
  "hashAlgo",
  "dhKey",
  "lifetime",
]);
const emit = defineEmits([
  "update:encryptAlgo",
  "update:hashAlgo",
  "update:dhKey",
  "update:lifetime",
]);
const { encryptAlgo, hashAlgo, dhKey, lifetime } = useVModels(props, emit);
</script>
