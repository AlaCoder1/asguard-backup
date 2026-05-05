<template>
  <h4>{{$t('Clientsopenvpn.UserAuthenticationSettings')}}</h4>
  <v-divider class="mt-2"></v-divider>
  <v-col align-self="center" cols="4">
    <label>{{$t('form.username')}}</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-text-field :label="$t('form.username')" v-model="username"></v-text-field>
  </v-col>
  <v-col class="mt-5"  cols="4">
    <label>{{$t('form.password')}}</label>
  </v-col>
  <v-col
    :cols="props.modeState === 'edit' ? 4 : 8"
    class="mb-n6"
  >
    <v-text-field
      :append-inner-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
      @click:append-inner="show1 = !show1"
      :type="show1 ? 'text' : 'password'"
      type="password"
      :label="$t('form.password')"
      v-model="password"
    ></v-text-field>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.passwordUser.$errors.length"
    >
      {{ props.errors.passwordUser.$errors?.[0].$message }}
    </p>
  </v-col>
  <v-col
    cols="4"
    class="mb-n6"
    v-if="props.modeState === 'edit'"
  >
    <v-text-field
      :append-inner-icon="show2 ? 'mdi-eye' : 'mdi-eye-off'"
      @click:append-inner="show2 = !show2"
      :type="show2 ? 'text' : 'password'"
      type="password"
      :label="$t('openvpn.newPassword')"
      v-model="NewUserPassword"
    ></v-text-field>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.NewUserPassword.$errors.length"
    >
      {{ props.errors.NewUserPassword.$errors?.[0].$message }}
    </p>
  </v-col>

  <v-col align-self="center" cols="4">
    <label>{{$t('Clientsopenvpn.Renegotiatetime')}}</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-text-field
      label="Renegotiate time"
      v-model="renegotiate_time"
    ></v-text-field>
  </v-col>
</template>

<script setup>
import { useVModels } from "@vueuse/core";
import { ref } from "vue";
const show1 = ref(false);
const show2 = ref(false);

const props = defineProps([
  "errors",
  "modeState",
  "username",
  "password",
  "NewUserPassword",
  "renegotiate_time",
]);

const emit = defineEmits([
  "update:username",
  "update:password",
  "update:NewUserPassword",
  "update:renegotiate_time",
]);

const { username, password, NewUserPassword, renegotiate_time } = useVModels(
  props,
  emit
);
</script>
