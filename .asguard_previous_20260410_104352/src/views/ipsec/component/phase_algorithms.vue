<template>
  <div class="ml-3 mr-3 mt-5">
    <h4>{{$t('PageIpsec.phase1_algorithm')}}</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4" class="mt-5">
        <label>{{$t('PageIpsec.algorithm_cryptage')}}*</label>
      </v-col>

      <template v-if="props.keyExchange.slug === 'V1'">
        <v-col cols="8" class="mb-n6">
          <v-select
            :label="$t('PageIpsec.algorithm_cryptage')"
            v-model="encryptAlgoV1"
            item-title="name"
            item-value="slug"
            return-object
            :items="props.filteredEncryptAlgoListV1"
          ></v-select>
          <p
            class="error-feedback mb-5"
            v-if="props.errors.encryptAlgoV1.$errors.length"
          >
            {{ props.errors.encryptAlgoV1.$errors?.[0].$message }}
          </p>
        </v-col>
      </template>

      <template v-else>
        <v-col cols="8" class="mb-n6">
          <v-select
            :label="$t('PageIpsec.algorithm_cryptage')"
            v-model="encryptAlgo"
            item-title="name"
            item-value="slug"
            return-object
            :items="props.filteredEncryptAlgoListV1"
          ></v-select>
          <p
            class="error-feedback mb-5"
            v-if="props.errors.encryptAlgo.$errors.length"
          >
            {{ props.errors.encryptAlgo.$errors?.[0].$message }}
          </p>
        </v-col>
      </template>

      <v-col cols="4" class="mt-5">
        <label>{{$t('PageIpsec.Hashalgorithm')}}*</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          :label="$t('PageIpsec.Hashalgorithm')"
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
        <label>{{$t('PageIpsec.DHkey')}}*</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          :label="$t('PageIpsec.DHkey')"
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
        <label>{{$t('PageIpsec.Lifetime')}}</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          :label="$t('PageIpsec.Lifetimeinseconds')"
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
  "keyExchange",
  "filteredEncryptAlgoListV1",
  "hashAlgoList",
  "encryptAlgoList",
  "dhKeyList",
  "encryptAlgoV1",
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
  "update:encryptAlgoV1",
]);
const { encryptAlgo, hashAlgo, dhKey, lifetime, encryptAlgoV1 } = useVModels(
  props,
  emit
);
</script>
