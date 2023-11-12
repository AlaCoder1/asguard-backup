<template>
  <h4>Cryptographic Settings</h4>
  <v-divider class="mt-3"></v-divider>
  <v-col cols="4" align-self="center">
    <label>TLS Authentification</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <input type="checkbox" v-model="isEnableAuth" />

    <label class="ml-2"
      >Automatically generate a shared TLS authentication key</label
    >
    <v-text-field
      v-if="!isEnableAuth"
      class="mt-3"
      v-model="tlsGenerate"
      label="shared TLS"
    ></v-text-field>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.tlsGenerate.$errors.length"
      >{{ props.errors.tlsGenerate.$errors?.[0].$message }}</p
    >
  </v-col>

  <v-col cols="4" align-self="center">
    <label>Peer Certificate Authority</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="Peer Certificate Authority"
      v-model="peerCertif"
      item-title="name"
      item-value="id"
      :items="state.mapedCertifAuth"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.peerCertif.$errors.length"
      >{{ props.errors.peerCertif.$errors?.[0].$message }}</p
    >
  </v-col>
  <v-col cols="4" align-self="center">
    <label>Serveur Certificate</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="Serveur Certificate"
      v-model="serverCertif"
      item-title="name"
      item-value="id"
      :items="state.mapedCertifServer"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.serverCertif.$errors.length"
      >{{ props.errors.serverCertif.$errors?.[0].$message }}</p
    >
  </v-col>
  <v-col cols="4" align-self="center">
    <label>DH Parameters Length algorithm</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="DH"
      v-model="dhParameters"
      :items="['2048', '4096']"
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.dhParameters.$errors.length"
      >{{ props.errors.dhParameters.$errors?.[0].$message }}</p
    >
  </v-col>
  <v-col cols="4" align-self="center">
    <label>Encryption algorithm</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="Algorithm"
      v-model="encryptAlgo"
      :items="[
        'AES-256-GCM',
        '192-AES-GCM',
        'AES-128-GCM',
        'CHACHA20-POLY1305',
      ]"
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.encryptAlgo.$errors.length"
      >{{ props.errors.encryptAlgo.$errors?.[0].$message }}</p
    >
  </v-col>
  <v-col cols="4" align-self="center">
    <label>Auth Digest Algorithm</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="Auth Digest Algorithm"
      v-model="authDigest"
      item-title="name"
      item-value="id"
      return-object
      :items="authDigestList"
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.authDigest.$errors.length"
      >{{ props.errors.authDigest.$errors?.[0].$message }}</p
    >
  </v-col>
  <v-col cols="4" align-self="center">
    <label>Hardware Crypto</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="Hardware Crypto"
      v-model="hardwareCrypto"
      item-title="name"
      :items="[
        { name: 'No hardware Crypto acceleration', slug: 'No Hardware Crypto' },
        { name: 'Intel RDRAND engine -RAND', slug: 'Intel RDRAND engine' },
      ]"
      return-object
    ></v-select>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.hardwareCrypto.$errors.length"
      >{{ props.errors.hardwareCrypto.$errors?.[0].$message }}</p
    >
  </v-col>
</template>

<script setup>
import axios from "axios";
import { onBeforeMount, reactive, ref } from "vue";
import { useVModels } from "@vueuse/core";

const props = defineProps([
  "errors",
  "tlsGenerate",
  "isEnableAuth",
  "peerCertif",
  "serverCertif",
  "dhParameters",
  "encryptAlgo",
  "authDigest",
  "hardwareCrypto",
]);
const emit = defineEmits([
  "update:isEnableAuth",
  "update:peerCertif",
  "update:serverCertif",
  "update:dhParameters",
  "update:encryptAlgo",
  "update:authDigest",
  "update:hardwareCrypto",
  "update:tlsGenerate",
]);
const {
  isEnableAuth,
  peerCertif,
  serverCertif,
  encryptAlgo,
  dhParameters,
  authDigest,
  hardwareCrypto,
  tlsGenerate,
} = useVModels(props, emit);

onBeforeMount(() => {
  getCertif();
  getAllCertAuth();
});

const state = reactive({
  authoritesData: null,
  certifData: null,
  mapedCertifAuth: [],
  mapedCertifServer: [],
});
const authDigestList = ref([
  {
    name: "BLAKE2b512",
    slug: "blake2b512",
    id: "1",
  },
  {
    name: "BLAKE2b256",
    slug: "blake2b256",
    id: "2",
  },
  {
    name: "SHA224",
    slug: "sha224",
    id: "3",
  },
  {
    name: "SHA256",
    slug: "sha256",
    id: "4",
  },
  {
    name: "SHA3-224",
    slug: "sha3-224",
    id: "5",
  },
  {
    name: "SHA3-256",
    slug: "sha3-256",
    id: "6",
  },
  {
    name: "SHA3-384",
    slug: "sha3-384",
    id: "7",
  },
  {
    name: "SHA3-512",
    slug: "sha3-512",
    id: "8",
  },

  {
    name: "SHA384",
    slug: "sha384",
    id: "9",
  },

  {
    name: "SHA512",
    slug: "sha512",
    id: "10",
  },
  {
    name: "SHA512-224",
    slug: "sha512-224",
    id: "11",
  },
  {
    name: "SHA512-256",
    slug: "sha512-256",
    id: "12",
  },
]);

const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

const getCertif = () => {
  const csrfToken = getCookie("csrftoken");
  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

  axios.get("/certificates/getAllCertificates").then(
    (response) => {
      let mapedListCertif = response.data.filter(
        (i) => i.certificate_type === "server"
      );
      state.mapedCertifServer = mapedListCertif.map((i) => {
        return {
          id: i.id,
          name: i.name,
        };
      });
    },
    (error) => {
      console.log(error);
    }
  );
};
const getAllCertAuth = () => {
  const csrfToken = getCookie("csrftoken");
  axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

  axios.get("/certificates/getAllCertAuth").then(
    (response) => {
      console.log("allcetAuth", response);
      let mapedList = response.data.map((i) => {
        return {
          id: i.id,
          name: i.name,
        };
      });
      state.mapedCertifAuth = mapedList;
    },
    (error) => {
      console.log(error);
    }
  );
};
</script>

<style lang="scss"></style>
