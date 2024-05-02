<template>
  <div>
    <v-card-title class="title-text">{{
      $t("interface.protocolTiming")
    }}</v-card-title>
    <v-divider class="ml-3"></v-divider>
    <table class="ml-3 mt-3 mr-5">
      <tbody>
        <tr>
          <td>
            <span style="color: black" class="">{{
              $t("interface.timeout")
            }}</span>
          </td>
          <td>
            <v-text-field
              :label="$t('interface.timeout')"
              class="ml-3 mt-1"
              v-model="timeout"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">{{
              $t("interface.tryAgain")
            }}</span>
          </td>
          <td style="width: 80%">
            <v-text-field
              :label="$t('interface.tryAgain')"
              class="ml-3 mt-1"
              v-model="retry"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black; width: 50%" class="">{{
              $t("interface.selectExpiration")
            }}</span>
          </td>
          <td style="width: 50%">
            <v-text-field
              :label="$t('interface.selectExpiration')"
              class="ml-3 mt-1"
              v-model="select_timeout"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">{{
              $t("interface.restart")
            }}</span>
          </td>
          <td style="width: 80%">
            <v-text-field
              :label="$t('interface.restart')"
              class="ml-3 mt-1"
              v-model="reboot"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">{{
              $t("interface.backoffCutoff")
            }}</span>
          </td>
          <td style="width: 80%">
            <v-text-field
              :label="$t('interface.backoffCutoff')"
              class="ml-3 mt-1"
              v-model="backoff"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">{{
              $t("interface.initialInterval")
            }}</span>
          </td>
          <td style="width: 80%">
            <v-text-field
              :label="$t('interface.initialInterval')"
              class="ml-3 mt-1"
              v-model="initial_interval"
            ></v-text-field>
          </td>
        </tr>
      </tbody>
    </table>
    <v-card-title class="title-text">{{
      $t("interface.leaseRequirements")
    }}</v-card-title>
    <v-divider class="ml-3"></v-divider>
    <table class="ml-3 mt-3 mr-5">
      <tbody>
        <tr>
          <td>
            <span style="color: black" class="">{{
              $t("interface.sendOptions")
            }}</span>
          </td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              :label="$t('interface.sendOptions')"
              v-model="dhcp_client"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">{{
              $t("interface.sendOptionsLeaseTime")
            }}</span>
          </td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              :label="$t('interface.sendOptionsLeaseTime')"
              v-model="lease_time"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">{{
              $t("interface.requestOptions")
            }}</span>
          </td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              :label="$t('interface.requestOptions')"
              v-model="request"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">{{
              $t("interface.requiredOptions")
            }}</span>
          </td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              :label="$t('interface.requiredOptions')"
              v-model="require"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">{{
              $t("interface.supersedeDomaineName")
            }}</span>
          </td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              :label="$t('interface.supersedeDomaineName')"
              v-model="domain_name"
            ></v-text-field>
          </td>
        </tr>
        <tr>
          <td>
            <span style="color: black" class="">{{$t('interface.prependDomainServer')}}</span>
          </td>
          <td style="width: 70%">
            <v-text-field
              class="ml-3 mt-1"
              :label="$t('interface.prependDomainServer')"
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
