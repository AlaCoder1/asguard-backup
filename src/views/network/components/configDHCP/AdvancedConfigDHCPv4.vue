<template>
  <div>
    <v-card-title class="title-text">Protocol Timing</v-card-title>
    <v-divider class="ml-3"></v-divider>
    <table class="ml-3 mt-3 mr-5">
      <tbody>
        <tr>
          <td><span style="color: black" class="">Timeout</span></td>
          <td>
            <v-text-field
              label="Enter Timeout"
              class="ml-3 mt-1"
              v-model="timeout"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td><span style="color: black" class="">Try again</span></td>
          <td style="width: 80%">
            <v-text-field
              label="Enter Try again"
              class="ml-3 mt-1"
              v-model="retry"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black; width: 50%" class=""
              >Select expiration</span
            >
          </td>
          <td style="width: 50%">
            <v-text-field
              label="Enter Select expiration"
              class="ml-3 mt-1"
              v-model="select_timeout"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td><span style="color: black" class="">Restart</span></td>
          <td style="width: 80%">
            <v-text-field
              label="Enter Restart"
              class="ml-3 mt-1"
              v-model="reboot"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td><span style="color: black" class="">Backoff Cutoff</span></td>
          <td style="width: 80%">
            <v-text-field
              label="Enter Backoff Cutoff"
              class="ml-3 mt-1"
              v-model="backoff"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td><span style="color: black" class="">Initial Interval</span></td>
          <td style="width: 80%">
            <v-text-field
              label="Enter Initial Interval"
              class="ml-3 mt-1"
              v-model="initial_interval"
            ></v-text-field>
          </td>
        </tr>
      </tbody>
    </table>
    <v-card-title class="title-text">Lease Requirements</v-card-title>
    <v-divider class="ml-3"></v-divider>
    <table class="ml-3 mt-3 mr-5">
      <tbody>
        <tr>
          <td>
            <span style="color: black" class="">Send options DHCP Client</span>
          </td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              label="Enter Send options DHCP Client"
              v-model="dhcp_client"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">Send Options lease time</span>
          </td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              label="Enter Send Options lease time"
              v-model="lease_time"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td><span style="color: black" class="">Request Options</span></td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              label="Enter Request Options"
              v-model="request"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td><span style="color: black" class="">Required Options</span></td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              label="Enter Required Options"
              v-model="require"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">Supersede domaine name</span>
          </td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              label="Enter Supersede domaine name"
              v-model="domain_name"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">Prepend domain server</span>
          </td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              label="Enter Prepend domain server"
              v-model="domain_server"
            ></v-text-field>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { useVModels } from "@vueuse/core";

const props = defineProps([
  "timeout",
  "retry",
  "select_timeout",
  "reboot",
  "backoff",
  "initial_interval",
  "dhcp_client",
  "lease_time",
  "request",
  "require",
  "domain_name",
  "domain_server",
]);

const emit = defineEmits([
  "update:timeout",
  "update:retry",
  "update:select_timeout",
  "update:reboot",
  "update:backoff",
  "update:initial_interval",
  "update:dhcp_client",
  "update:lease_time",
  "update:request",
  "update:require",
  "update:domain_name",
  "update:domain_server",
]);

const {
  timeout,
  retry,
  select_timeout,
  reboot,
  backoff,
  initial_interval,
  dhcp_client,
  lease_time,
  request,
  require,
  domain_name,
  domain_server,
} = useVModels(props, emit);
</script>

<style scoped>
.title-text {
  color: #020202;
  font-family: Nunito;
  font-size: 18px;
  font-style: normal;
  font-weight: 700;
  line-height: normal;
}
</style>
