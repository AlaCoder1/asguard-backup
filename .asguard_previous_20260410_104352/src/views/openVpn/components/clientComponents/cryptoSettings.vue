<template>
  <h4>{{$t('openvpn.CryptographicSettings')}}</h4>
  <v-divider class="mt-2"></v-divider>
  <v-col cols="4">
    <label>{{$t('openvpn.TLSAuthentication')}}</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <input type="checkbox" v-model="tlsGenerate" />
    <label class="ml-2"
      >{{$t('openvpn.automatiquegen')}}</label
    >
  </v-col>
  <template v-if="!tlsGenerate">
    <v-col align-self="center" cols="4"> </v-col>
    <v-col align-self="center" cols="8" class="mb-n6">
      <v-textarea
        class="mt-3"
        v-model="sharedKey"
        :label="$t('Clientsopenvpn.TLSkey')"
        variant="outlined"
      ></v-textarea>
      <p
        class="error-feedback mb-5"
        v-if="props.errors.sharedKey.$errors.length"
      >
        {{ props.errors.sharedKey.$errors?.[0].$message }}
      </p>
    </v-col>
  </template>
  <v-col align-self="center" cols="4">
    <label>{{$t('openvpn.peercertif')}}*</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-select
      :label="$t('openvpn.peercertif')"
      v-model="peerCertificateAuthority"
      item-title="name"
      item-value="id"
      :items="props.mapedCertifAuth"
      :no-data-text="$t('certificat.certificatlist')"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.peerCertificateAuthority.$errors.length"
    >
      {{ props.errors.peerCertificateAuthority.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col align-self="center" cols="4">
    <label>{{$t('Clientsopenvpn.ClientCertificate')}}*</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-select
      :label="$t('Clientsopenvpn.ClientCertificate')"
      :no-data-text="$t('certificat.certificatlist')"
      v-model="clientCertificate"
      item-title="name"
      item-value="id"
      :items="props.clientCertificateList"
      return-object
      

    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.clientCertificate.$errors.length"
    >
      {{ props.errors.clientCertificate.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col align-self="center" cols="4">
    <label>{{$t('PageIpsec.algorithm_cryptage')}}*</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-select
      :label="$t('PageIpsec.algorithm_cryptage')"
      v-model="encryptionAlgorithm"
      :items="encryptionAlgorithmList"
      item-title="name"
      item-value="slug"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.encryptionAlgorithm.$errors.length"
    >
      {{ props.errors.encryptionAlgorithm.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col align-self="center" cols="4">
    <label>{{$t('openvpn.Auth_diagest')}}*</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-select
      :label="$t('openvpn.Auth_diagest')"
      v-model="authDigestAlgorithm"
      item-title="name"
      item-value="slug"
      :items="authDigestAlgorithmList"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.authDigestAlgorithm.$errors.length"
    >
      {{ props.errors.authDigestAlgorithm.$errors?.[0].$message }}
    </p>
  </v-col>
  <!-- <v-col align-self="center" cols="4">
    <label>Hardware Crypto</label>
  </v-col> -->
  <v-col align-self="center" cols="8" class="mb-n6">
    <!-- <v-select
      label="Hardware Crypto"
      v-model="hardwareCrypto"
      :items="hardwareCryptoList"
      item-title="name"
      item-value="slug"
      return-object
    ></v-select> -->
    <!-- <p
      class="error-feedback mb-5"
      v-if="props.errors.hardwareCrypto.$errors.length"
    >
      {{ props.errors.hardwareCrypto.$errors?.[0].$message }}
    </p> -->
  </v-col>
</template>

<script setup>
import { useVModels } from "@vueuse/core";
import axios from "axios";
import { onBeforeMount, ref, reactive } from "vue";

const encryptionAlgorithmList = ref([
  {
    name: "AES-256-GCM",
    slug: "AES-256-GCM",
  },
  {
    name: "AES-128-GCM",
    slug: "AES-128-GCM",
  },
  {
    name: "CHACHA20-POLY1305",
    slug: "CHACHA20-POLY1305",
  },
]);
const authDigestAlgorithmList = ref([
  {
    name: "SHA224",
    slug: "sha224",
  },
  {
    name: "SHA256",
    slug: "SHA256",
  },
  {
    name: "SHA384",
    slug: "SHA384",
  },

  {
    name: "SHA512",
    slug: "SHA512",
  },
  {
    name: "SHA3-224",
    slug: "SHA3-224",
  },
  {
    name: "SHA3-256",
    slug: "SHA3-256",
  },
  {
    name: "SHA3-384",
    slug: "SHA3-384",
  },
  {
    name: "SHA3-512",
    slug: "SHA3-512",
  },
]);
const hardwareCryptoList = ref([
  {
    name: "No Hardware Crypto acceleration",
    slug: "No Hardware Crypto",
  },
  {
    name: "Intel RDRAND engine -RAND",
    slug: "Intel RDRAND engine -RAND",
  },
]);


const props = defineProps([
  "errors",
  "clientCertificateList",
  "mapedCertifAuth",
  "tlsGenerate",
  "sharedKey",
  "peerCertificateAuthority",
  "clientCertificate",
  "encryptionAlgorithm",
  "authDigestAlgorithm",
  "hardwareCrypto",
]);

const emit = defineEmits([
  "update:tlsGenerate",
  "update:peerCertificateAuthority",
  "update:serverCertif",
  "update:dhParameters",
  "update:encryptAlgo",
  "update:authDigest",
  "update:hardwareCrypto",
]);

const {
  tlsGenerate,
  sharedKey,
  peerCertificateAuthority,
  clientCertificate,
  encryptionAlgorithm,
  authDigestAlgorithm,
  hardwareCrypto,
} = useVModels(props, emit);

</script>
