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
          :items="props.protocolListph2"
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
            :items="props.encryptAlgoListExchange"
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
          :items="props.hashAlgoList"
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
          :items="props.pfsList"
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
          label="Lifetime in seconds"
          v-model="lifetimeExchange"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.lifetimeExchange.$errors.length"
        >
          {{ props.errors.lifetimeExchange.$errors?.[0].$message }}
        </p>
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

const props = defineProps([
  "protocolListph2",
  "pfsList",
  "encryptAlgoListExchange",
  "hashAlgoList",
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
