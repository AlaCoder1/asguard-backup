<template>
  <div class="ml-3 mr-3 mt-5">
    <h4>{{$t("PageIpsec.proposal_pahse1")}}</h4>
    <v-divider class="mt-2"></v-divider>
    <v-row class="mt-2">
      <v-col cols="4" class="mt-5">
        <label>{{$t('PageIpsec.Authenticationmethod')}}*</label>
      </v-col>
      <v-col cols="8" class="mb-n6">
        <v-select
          :label="$t('PageIpsec.Authenticationmethod')"
          v-model="authMethod"
          item-title="name"
          item-value="slug"
          return-object
          :items="props.authenticationMethodList"
        ></v-select>
        <p
          class="error-feedback mb-5"
          v-if="props.errors.authMethod.$errors.length"
        >
          {{ props.errors.authMethod.$errors?.[0].$message }}
        </p>
      </v-col>
      <template v-if="props.keyExchange?.slug === 'V1'">
        <v-col cols="4" class="mt-5">
          <label>{{$t('PageIpsec.modenegociation')}}*</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-select
            :label="$t('PageIpsec.modenegociation')"
            v-model="negotiationMode"
            item-title="name"
            item-value="slug"
            return-object
            :items="props.negotiationList"
          ></v-select>
          <p
            class="error-feedback mb-5"
            v-if="props.errors.negotiationMode.$errors.length"
          >
            {{ props.errors.negotiationMode.$errors?.[0].$message }}
          </p>
        </v-col>
      </template>
      <template v-if="props.authMethodItem?.slug === 'Mutual PSK'">
        <v-col cols="4" class="mt-6">
          <label>{{$t('PageIpsec.SharedKey')}}*</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-textarea
            rows="1"
            row-height="15"
            class="mt-3"
            v-model="sharedKey"
            :label="$t('PageIpsec.SharedKey')"
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
      <template v-if="props.authMethodItem?.slug === 'Mutual RSA'">
        <v-col cols="4" class="mt-5">
          <label>{{$t('PageIpsec.mycertificat')}}*</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-select
            v-model="certificate"
            :label="$t('PageIpsec.mycertificat')"
            item-title="name"
            item-value="id"
            :no-data-text="$t('certificat.certificatlist')"
            :items="props.CertificateList"
            return-object
          ></v-select>
          <p
            class="error-feedback mb-5"
            v-if="props.errors.certificate.$errors.length"
          >
            {{ props.errors.certificate.$errors?.[0].$message }}
          </p>
        </v-col>

        <v-col cols="4" class="mt-5">
          <label>{{$t('PageIpsec.RemoteCertificate')}}* <br /> </label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-select
            v-model="peerIdentifier"
            :label="$t('PageIpsec.RemoteCertificate')"
            item-title="name"
            item-value="id"
            :no-data-text="$t('certificat.certificatlist')"
            :items="props.CertificateListRemote"
            return-object
          ></v-select>

          <p
            class="error-feedback mb-5"
            v-if="props.errors.peerIdentifier.$errors.length"
          >
            {{ props.errors.peerIdentifier.$errors?.[0].$message }}
          </p>
        </v-col>
      </template>
      <template v-if="props.authMethodItem?.slug === 'Mutual Public key'">
        <v-col cols="4" class="mt-5">
          <label>{{ $t('PageIpsec.LocalKeyPair') }}*</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-select
            v-model="localKey"
            :label="$t('PageIpsec.LocalKeyPair')"
            item-title="name"
            item-value="id"
            :no-data-text="$t('certificat.certificatlist')"
            :items="props.mapedKeyPublic"
            return-object
          ></v-select>
          <p
            class="error-feedback mb-5"
            v-if="props.errors.localKey.$errors.length"
          >
            {{ props.errors.localKey.$errors?.[0].$message }}
          </p>
        </v-col>
        <v-col cols="4" class="mt-5">
          <label>{{$t('PageIpsec.PeerKeyPair')}}*</label>
        </v-col>
        <v-col cols="8" class="mb-n6">
          <v-select
            v-model="keyPair"
            :label="$t('PageIpsec.PeerKeyPair')"
            item-title="name"
            item-value="id"
            :no-data-text="$t('certificat.certificatlist')"
            :items="props.mapedKeyPublic"
            return-object
          ></v-select>
          <p
            class="error-feedback mb-5"
            v-if="props.errors.keyPair.$errors.length"
          >
            {{ props.errors.keyPair.$errors?.[0].$message }}
          </p>
        </v-col>
      </template>
    </v-row>
    <v-row class="mt-2">
      <div class="ml-3 mr-3">
        <v-row class="mt-2"> </v-row>
      </div>
    </v-row>
    <v-spacer></v-spacer>
  </div>
</template>
<script setup>
import { useVModels } from "@vueuse/core";

const props = defineProps([
  "mapedKeyPublic",
  "CertificateList",
  "CertificateListRemote",
  "negotiationList",
  "authMethodItem",
  "keyExchange",
  "authenticationMethodList",
  "errors",
  "authMethod",
  "negotiationMode",
  "sharedKey",
  "localKey",
  "certificate",
  "peerIdentifier",
  "keyPair",
]);
const emit = defineEmits([
  "update:authMethod",
  "update:negotiationMode",
  "update:sharedKey",
  "update:localKey",
  "update:certificate",
  "update:keyPair",
  "update:peerIdentifier",
]);
const {
  authMethod,
  negotiationMode,
  sharedKey,
  certificate,
  keyPair,
  localKey,
  peerIdentifier,
} = useVModels(props, emit);
</script>
