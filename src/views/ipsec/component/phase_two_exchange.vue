<template>
  <div class="ml-3 mr-3 mt-5">
    <h4>Phase 2 proposal (SA/Key Exchange)</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4" class="mt-5">
        <label>Protocol</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Protocol"
          v-model="protocol"
          item-title="name"
          item-value="slug"
          return-object
          :items="[
            {
              name: 'ESP',
              slug: 'ESP',
            },
            { name: 'AH', slug: 'AH' },
          ]"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.protocol.$errors.length"
        >
          {{ props.errors.protocol.$errors?.[0].$message }}
        </p>
      </v-col>
      <template v-if="props.isProtocol?.slug === 'ESP'">
        <v-col cols="4" class="mt-5">
          <label>Encryption algorithms</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-select
            label="Encryption algorithms"
            v-model="encryptAlgoExchange"
            item-title="name"
            item-value="slug"
            return-object
            multiple
            :items="encryptAlgoList"
          ></v-select>
          <p
            class="error-feedback mb-5"
            v-if="props.errors.encryptAlgoExchange.$errors.length"
          >
            {{ props.errors.encryptAlgoExchange.$errors?.[0].$message }}
          </p>
        </v-col>
      </template>
      <v-col cols="4" class="mt-5">
        <label>Hash algorithms</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Hash algorithms"
          v-model="hashAlgoExchange"
          item-title="name"
          item-value="slug"
          return-object
          multiple
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
          v-if="props.errors.hashAlgoExchange.$errors.length"
        >
          {{ props.errors.hashAlgoExchange.$errors?.[0].$message }}
        </p>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>PFS key group</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="PFS key group"
          v-model="pfsKey"
          item-title="name"
          item-value="slug"
          return-object
          :items="pfsList"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.pfsKey.$errors.length"
        >
          {{ props.errors.pfsKey.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Lifetime</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Lifetime"
          v-model="lifetimeExchange"
        ></v-text-field>
      </v-col>
      <!-- <template v-if="false">
        <v-col cols="12">
          <h4>Advanced Options</h4>
          <v-divider class="mt-2"></v-divider>
        </v-col>
        <v-col cols="4" class="mt-5">
          <label>Automatically ping host</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-text-field
            label="Automatically ping host"
            v-model="pingHost"
          ></v-text-field>
          <p
            class="error-feedback mb-5"
            v-if="props.errors.pingHost.$errors.length"
          >
            {{ props.errors.pingHost.$errors?.[0].$message }}
          </p>
        </v-col>
        <v-col cols="4" class="mt-5">
          <label>Manual SPD entries</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-text-field
            label="Manual SPD entries"
            v-model="spdEntries"
          ></v-text-field>
          <p
            class="error-feedback mb-5"
            v-if="props.errors.spdEntries.$errors.length"
          >
            {{ props.errors.spdEntries.$errors?.[0].$message }}
          </p>
        </v-col>
      </template> -->
    </v-row>
  </div>
</template>
<script setup>
import { ref } from "vue";
import { useVModels } from "@vueuse/core";

const pfsList = ref([
  {
    name: "off",
    slug: "off",
  },
  { name: "15 (3072 bits)", slug: "15:3072" },
  { name: "16 (4096 bits)", slug: "16:4096" },
  { name: "17 (6144 bits)", slug: "17:6144" },
  { name: "18 (8192 bits)", slug: "18:8192" },
  { name: "19 (NIST EC 256 bits)", slug: "19:256" },
  { name: "20 (NIST EC 384 bits)", slug: "20:384" },
  { name: "21 (NIST EC 521 bits)", slug: "21:521" },
  { name: "28 (Brainpool EC 256 bits)", slug: "28:256" },
  { name: "29 (Brainpool EC 384 bits)", slug: "29:384" },
  { name: "30 (Brainpool EC 512 bits)", slug: "30:512" },
  { name: "31 (Elliptic Curve 25519)", slug: "31:25519" },
]);

const encryptAlgoList = ref([
  {
    name: "aes128gcm16",
    slug: "128",
  },
  {
    name: "aes192gcm16",
    slug: "192",
  },
  {
    name: "aes256gcm16",
    slug: "256",
  },
]);

const props = defineProps([
  "isProtocol",
  "isMode",
  "errors",
  "spdEntries",
  "protocol",
  "encryptAlgoExchange",
  "hashAlgoExchange",
  "pfsKey",
  "pingHost",
  "lifetimeExchange",
]);
const emit = defineEmits([
  "update:protocol",
  "update:pingHost",
  "update:spdEntries",
  "update:encryptAlgoExchange",
  "update:hashAlgoExchange",
  "update:pfsKey",
  "update:lifetimeExchange",
]);
const {
  protocol,
  encryptAlgoExchange,
  hashAlgoExchange,
  pfsKey,
  lifetimeExchange,
  pingHost,
  spdEntries,
} = useVModels(props, emit);
</script>
