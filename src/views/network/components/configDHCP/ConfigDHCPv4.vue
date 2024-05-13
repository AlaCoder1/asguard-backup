<template>
  <div class="mt-5 mb-5">
    <v-row>
      <v-col cols="12">
        <div class="mr-2 ml-2">
          <v-row class="mt-2">
            <v-col cols="12">
              <v-text-field
                :model-value="ipAddress"
                :label="$t('interface.IPV4Address')"
                variant="outlined"
                readonly
              ></v-text-field>
            </v-col>
            <v-col align-self="center" cols="4">
              <label class="ml-2">{{ $t("interface.IPV4Address") }}</label>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-text-field
                :label="$t('interface.IPV4Address')"
                v-model="alias_add"
                class="ip-address-style"
              ></v-text-field>
            </v-col>
            <v-col cols="4" class="mb-n6">
              <v-select
                v-model="alias_mask"
                :items="netmasks"
                :no-data-text="$t('certificat.certificatlist')"
                class="ml-3 netmask-select-style"
              ></v-select>
            </v-col>
            <v-col align-self="center" cols="4">
              <label class="ml-2">{{ $t("interface.rejectLeasesFrom") }}</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                :label="$t('interface.rejectLeasesFrom')"
                v-model="rejectLeases"
              ></v-text-field>
            </v-col>
            <v-col align-self="center" cols="4">
              <label class="ml-2">{{ $t("interface.hostname") }}</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-text-field
                :label="$t('interface.hostname')"
                v-model="hostname"
              ></v-text-field>
            </v-col>
            <v-col align-self="center" cols="4">
              <label class="ml-2">{{ $t("interface.overrideMTU") }}</label>
            </v-col>
            <v-col cols="8" class="mb-n6">
              <v-checkbox
                v-model="overrideMTU"
                :label="$t('interface.overrideMTU')"
              ></v-checkbox>
            </v-col>
          </v-row>
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { useVModels } from "@vueuse/core";
import { ref } from "vue";
import netmaskItems from "../../../../constants/netmask.js";

const netmasks = ref(netmaskItems);

const props = defineProps([
  "errors",
  "ipAddress",
  "alias_add",
  "alias_mask",
  "rejectLeases",
  "hostname",
  "overrideMTU",
]);

const emit = defineEmits([
  "update:alias_add",
  "update:alias_mask",
  "update:rejectLeases",
  "update:hostname",
  "update:overrideMTU",
]);

const { alias_add, alias_mask, rejectLeases, hostname, overrideMTU } =
  useVModels(props, emit);
</script>
