<template>
  <h4>Cryptographic Settings</h4>
  <v-divider class="mt-3"></v-divider>
  <v-col cols="4">
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
      label="Text"
    ></v-text-field>
  </v-col>

  <v-col cols="4">
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
  </v-col>
  <v-col cols="4">
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
  </v-col>
  <v-col cols="4">
    <label>DH Parameters Length algorithm</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select
      label="DH"
      v-model="dhParameters"
      :items="['2048', '4096']"
    ></v-select>
  </v-col>
  <v-col cols="4">
    <label>Encryption algorithm</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select label="Algorithm" v-model="encryptAlgo"></v-select>
  </v-col>
  <v-col cols="4">
    <label>Auth Digest Algorithm</label>
  </v-col>
  <v-col cols="8" class="mb-n6">
    <v-select label="Auth Digest Algorithm" v-model="authDigest"></v-select>
  </v-col>
  <v-col cols="4">
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
  </v-col>
</template>

<script setup>
import axios from "axios";
import { onBeforeMount, reactive, ref } from "vue";
import { useVModels } from "@vueuse/core";

const props = defineProps([
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
const mapList = ref(null);

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
