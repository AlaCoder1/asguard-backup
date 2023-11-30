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
          :items="props.encryptAlgoList"
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
          :items="props.hashAlgoList"
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
          :items="props.dhKeyList"
        ></v-select>
        <p class="error-feedback mb-5" v-if="props.errors.dhKey.$errors.length">
          {{ props.errors.dhKey.$errors?.[0].$message }}
        </p>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Lifetime</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Lifetime in seconds"
          v-model="lifetime"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.lifetime.$errors.length"
        >
          {{ props.errors.lifetime.$errors?.[0].$message }}
        </p>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
import { useVModels } from "@vueuse/core";

const props = defineProps([
  "hashAlgoList",
  "encryptAlgoList",
  "dhKeyList",
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
