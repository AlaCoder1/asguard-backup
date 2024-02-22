<template>
  <h4>User Authentication Settings</h4>
  <v-divider class="mt-2"></v-divider>
  <v-col align-self="center" cols="4">
    <label>Username</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-text-field label="Username" v-model="username"></v-text-field>
  </v-col>
  <v-col align-self="center" cols="4">
    <label>Password</label>
  </v-col>
  <v-col align-self="center" cols="8" class="mb-n6">
    <v-text-field
      type="password"
      label="Password"
      v-model="password"
    ></v-text-field>
    <p
      class="error-feedback mb-5"
      v-if="props.errors.passwordUser.$errors.length"
    >
      {{ props.errors.passwordUser.$errors?.[0].$message }}
    </p>
  </v-col>

  <v-col align-self="center" cols="4">
    <label>Renegotiate time</label>
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

const props = defineProps([
  "errors",
  "username",
  "password",
  "renegotiate_time",
]);

const emit = defineEmits([
  "update:username",
  "update:password",
  "update:renegotiate_time",
]);

const { username, password, renegotiate_time } = useVModels(props, emit);
</script>
