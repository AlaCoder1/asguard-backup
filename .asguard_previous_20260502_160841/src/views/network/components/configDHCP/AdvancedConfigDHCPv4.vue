<template>

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
