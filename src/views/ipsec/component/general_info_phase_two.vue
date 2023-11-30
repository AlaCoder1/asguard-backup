<template>
  <div class="ml-3 mr-3">
    <h4>General information phase2</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4" class="mt-5">
        <label>Mode</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          label="Mode"
          v-model="mode"
          item-title="name"
          item-value="slug"
          return-object
          :items="props.modeList"
        ></v-select>
        <p class="error-feedback mb-5" v-if="props.errors.mode.$errors.length">
          {{ props.errors.mode.$errors?.[0].$message }}
        </p>
      </v-col>
      <v-col cols="4" class="mt-5">
        <label>Description</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field label="description" v-model="description"></v-text-field>
      </v-col>
      <!-- <template>
      <v-col cols="12">
        <h4>Tunnel network</h4>
        <v-divider class="mt-2"></v-divider>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Local Address</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Local Address"
          v-model="localAddress"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.localAddress.$errors.length"
        >
          {{ props.errors.localAddress.$errors?.[0].$message }}
        </p>
      </v-col>

      <v-col cols="4" class="mt-5">
        <label>Remote Address</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-text-field
          label="Remote Address"
          v-model="remoteTunnelAddress"
        ></v-text-field>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.remoteTunnelAddress.$errors.length"
        >
          {{ props.errors.remoteTunnelAddress.$errors?.[0].$message }}
        </p>
      </v-col>
    </template> -->
      <template
        v-if="
          props.isMode?.slug === 'Tunnel IPv4' ||
          props.isMode?.slug === 'Tunnel IPv6'
        "
      >
        <v-col cols="12">
          <h4>Local network</h4>
          <v-divider class="mt-2"></v-divider>
        </v-col>

        <v-col cols="4" class="mt-5">
          <label>Type</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-select
            label="Type"
            v-model="type"
            item-title="name"
            item-value="slug"
            return-object
            :items="props.mapedInterfaceType"
          ></v-select>
          <p
            class="error-feedback mb-5"
            v-if="props.errors.type.$errors.length"
          >
            {{ props.errors.type.$errors?.[0].$message }}
          </p>
        </v-col>

        <v-col class="mt-5" cols="4">
          <label>Address</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-row>
            <v-col cols="7">
              <v-text-field
                label="Address"
                :readonly="props.isTypeWAn"
                v-model="localNetworkAddress"
              ></v-text-field>

              <p
                class="error-feedback mb-5"
                v-if="props.errors.localNetworkAddress.$errors.length"
              >
                {{ props.errors.localNetworkAddress.$errors?.[0].$message }}
              </p>
            </v-col>
            <v-col cols="1">
              <div class="ml-1 mt-5">/</div>
            </v-col>
            <v-col cols="4">
              <v-select
                :label="props.defaultValue ?? 'Address'"
                :readonly="props.isTypeWAn || props.isDefault"
                v-model="selectAddressNetwork"
                :items="props.numberList"
              ></v-select>
              <p
                class="error-feedback mb-5"
                v-if="props.errors.selectAddressNetwork.$errors.length"
              >
                {{ props.errors.selectAddressNetwork.$errors?.[0].$message }}
              </p>
            </v-col>
          </v-row>
        </v-col>

        <v-col cols="12">
          <h4>Remote Network</h4>
          <v-divider class="mt-2"></v-divider>
        </v-col>

        <v-col cols="4" class="mt-5">
          <label>Type</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-select
            label="Type"
            v-model="typeRemoteNetwork"
            item-title="name"
            item-value="slug"
            return-object
            :items="props.remoteTypeList"
          ></v-select>
          <p
            class="error-feedback mb-5"
            v-if="props.errors.typeRemoteNetwork.$errors.length"
          >
            {{ props.errors.typeRemoteNetwork.$errors?.[0].$message }}
          </p>
        </v-col>

        <v-col class="mt-5" cols="4">
          <label>Address</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-row>
            <v-col cols="7">
              <v-text-field
                label="Address"
                v-model="remoteNetworkAddress"
              ></v-text-field>

              <p
                class="error-feedback mb-5"
                v-if="props.errors.remoteNetworkAddress.$errors.length"
              >
                {{ props.errors.remoteNetworkAddress.$errors?.[0].$message }}
              </p>
            </v-col>
            <v-col cols="1">
              <div class="ml-1 mt-5">/</div>
            </v-col>
            <v-col cols="4">
              <v-select
                :label="props.defaultValueRemote ?? 'Address'"
                :readonly="props.isDefaultRemote"
                v-model="selectRemoteAddressNetwork"
                :items="props.numberList"
              ></v-select>
              <p
                class="error-feedback mb-5"
                v-if="props.errors.selectRemoteAddressNetwork.$errors.length"
              >
                {{
                  props.errors.selectRemoteAddressNetwork.$errors?.[0].$message
                }}
              </p>
            </v-col>
          </v-row>
        </v-col>
      </template>
    </v-row>
  </div>
</template>
<script setup>
import { useVModels } from "@vueuse/core";

const props = defineProps([
  "remoteTypeList",
  "mapedInterfaceType",
  "numberList",
  "modeList",
  "defaultValueRemote",
  "isDefaultRemote",
  "defaultValue",
  "isDefault",
  "isTypeWAn",
  "isMode",
  "errors",
  "mode",
  "description",
  "remoteTunnelAddress",
  "type",
  "localNetworkAddress",
  "selectAddressNetwork",
  "selectRemoteAddressNetwork",
  "typeRemoteNetwork",
  "remoteNetworkAddress",
  "localAddress",
]);
const emit = defineEmits([
  "update:mode",
  "update:remoteTunnelAddress",
  "update:type",
  "update:localAddress",
  "update:localNetworkAddress",
  "update:selectAddressNetwork",
  "update:selectRemoteAddressNetwork",
  "update:description",
  "update:typeRemoteNetwork",
  "update:remoteNetworkAddress",
]);
const {
  mode,
  remoteTunnelAddress,
  type,
  remoteNetworkAddress,
  selectAddressNetwork,
  description,
  localAddress,
  localNetworkAddress,
  selectRemoteAddressNetwork,
  typeRemoteNetwork,
} = useVModels(props, emit);
</script>
