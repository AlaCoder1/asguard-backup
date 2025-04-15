<template>
  <div class="mt-2 mr-5 d-flex justify-end cursor-pointer">
    <span
      @click="openModal"
      style="cursor: pointer; font-size: 30px; color: #213e9f"
      class="mdi mdi-help-circle-outline cursor-pointer"
    ></span>
  </div>
  <div>
    <v-row justify="center">
      <v-dialog v-model="state.openModal" width="800">
        <form ref="myForm" @submit.prevent="submitForm" class="scroller">
          <v-card>
            <v-card-title> </v-card-title>
            <v-card-text>
              <v-container>
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="headline text-black"> </span>
                  <span
                    style="font-size: 24px"
                    class="mdi mdi-close cursor-pointer text-black"
                    @click="state.openModal = false"
                  ></span>
                </div>
                <div
                  v-if="help === 'subscription'"
                  style="display: flex; justify-content: center"
                >
                  <subscription />
                </div>
                <div v-if="help === 'users'">
                  <users />
                </div>
                <div v-if="help === 'certificates'">
                  <certificates />
                </div>
                <div v-if="help === 'key-pair'">
                  <keyPair />
                </div>
                <div v-if="help === 'list-interfaces'">
                  <listInter />
                </div>
                <div v-if="help === 'type-interfaces'">
                  <typeInter />
                </div>
                <div v-if="help === 'dhcp'">
                  <dhcp />
                </div>
                <div v-if="help === 'routing'">
                  <routing />
                </div>
                <div v-if="help === 'rules'">
                  <rules />
                </div>
                <div v-if="help === 'snat'">
                  <snat />
                </div>
                <div v-if="help === 'one'">
                  <one />
                </div>
                <div v-if="help === 'dnat'">
                  <dnat />
                </div>
                <div v-if="help === 'config'">
                  <config />
                </div>
                <div v-if="help === 'listing'">
                  <listingIPSEC />
                </div>
                <div v-if="help === 'monitoring'">
                  <monitoring />
                </div>
                <div v-if="help === 'serverVPN'">
                  <serverVPN />
                </div>
                <div v-if="help === 'clientVPN'">
                  <clientVPN />
                </div>
                <div v-if="help === 'config-suricata'">
                  <configSuricata />
                </div>
                <div v-if="help === 'suricata-rules'">
                  <suricataRules />
                </div>
                <div v-if="help === 'suricata-alerts'">
                  <suricataAlerts />
                </div>
                <div v-if="help === 'proxy'">
                  <proxy />
                </div>
                <div v-if="help === 'wafConfig'">
                  <wafConfig />
                </div>
                <div v-if="help === 'wafRules'">
                  <wafRules />
                </div>
                <div v-if="help === 'wafalerts'">
                  <wafalerts />
                </div>
                <div v-if="help === 'wafApplications'">
                  <wafApplications />
                </div>
                <div v-if="help === 'sdwan'">
                  <sdwan />
                </div>
                <div v-if="help === 'ztnaIdentities'">
                  <ztnaIdentities />
                </div>
                <div v-if="help === 'ztnaConfigurations'">
                  <configurations />
                </div>
                <div v-if="help === 'ztnaServices'">
                  <services />
                </div>
                <div v-if="help === 'ztnaRelays'">
                  <relays />
                </div>
                <div v-if="help === 'ztnaPolicies'">
                  <policies />
                </div>
                <div v-if="help === 'settings'">
                  <settings />
                </div>
              </v-container>
            </v-card-text>

            <v-card-actions class="mt-3 actionBtn">
              <v-spacer></v-spacer>

              <v-btn
                color="indigo-darken-3"
                :rounded="true"
                large
                outlined
                label-color="#213E9F"
                variant="flat"
                class="mt-3 btn-add"
                text
                @click="state.openModal = false"
              >
                <span class="pr-3 pl-3">{{ $t("buttons.close") }}</span></v-btn
              >
            </v-card-actions>
          </v-card>
        </form>
      </v-dialog>
    </v-row>
  </div>
</template>

<script>
import { reactive, toRefs } from "vue";
import subscription from "@/views/help/subscription.vue";
import certificates from "@/views/help/certificates.vue";
import keyPair from "@/views/help/key-pair.vue";
import users from "@/views/help/users.vue";
import listInter from "@/views/help/interfaces/list-interfaces.vue";
import typeInter from "@/views/help/interfaces/type_interfaces.vue";
import dhcp from "@/views/help/interfaces/dhcp.vue";
import routing from "@/views/help/interfaces/routing.vue";
import rules from "@/views/help/rules.vue";
import snat from "@/views/help/nat/snat.vue";
import one from "@/views/help/nat/oneTone.vue";
import dnat from "@/views/help/nat/dnat.vue";
import config from "@/views/help/ipsec/config.vue";
import listingIPSEC from "@/views/help/ipsec/listing.vue";
import monitoring from "@/views/help/ipsec/monitoring.vue";
import serverVPN from "@/views/help/openvpn/servers.vue";
import clientVPN from "@/views/help/openvpn/clients.vue";
import configSuricata from "@/views/help/suricata/config.vue";
import suricataRules from "@/views/help/suricata/rules.vue";
import suricataAlerts from "@/views/help/suricata/alerts.vue";
import proxy from "@/views/help/proxy.vue";
import wafConfig from "@/views/help/waf/config.vue";
import wafRules from "@/views/help/waf/rules.vue";
import wafalerts from "@/views/help/waf/alerts.vue";
import wafApplications from "@/views/help/waf/applications.vue";
import sdwan from "@/views/help/sdwan.vue";
import ztnaIdentities from "@/views/help/ztna/identities.vue";
import configurations from "@/views/help/ztna/configurations.vue";
import services from "@/views/help/ztna/services.vue";
import relays from "@/views/help/ztna/relays.vue";
import policies from "@/views/help/ztna/policies.vue";
import settings from "@/views/help/settings.vue";

export default {
  components: {
    ztnaIdentities,
    configurations,
    services,
    relays,
    policies,
    subscription,
    certificates,
    users,
    rules,
    snat,
    dnat,
    one,
    keyPair,
    listInter,
    dhcp,
    typeInter,
    routing,
    config,
    listingIPSEC,
    monitoring,
    serverVPN,
    clientVPN,
    configSuricata,
    suricataRules,
    suricataAlerts,
    proxy,
    wafConfig,
    wafRules,
    wafalerts,
    wafApplications,
    sdwan,
    settings,
  },
  props: {
    help: {
      type: Object,
      Array,
      String,
      required: true,
    },
  },

  setup(props) {
    const { help } = toRefs(props);

    const state = reactive({
      openModal: false,
    });

    const openModal = () => {
      state.openModal = true;
    };

    return {
      state,
      openModal,
    };
  },
};
</script>
<style>
.scroller {
  overflow: auto;
}
</style>
