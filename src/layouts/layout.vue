<template>
  <!-- <v-app id="inspire">
    <TheSidebarVue style="width: auto;"/>
    <TheHeadingVue />
    <v-main >
      <v-toolbar dark fixed app class="asguard_toolbar">
        <v-toolbar-title>
          {{ title }}
        </v-toolbar-title>
        <v-spacer />
        <div v-if="back">
          <v-btn>
            {{ titleback }}
          </v-btn>
        </div>
      </v-toolbar>
      <slot name="content"></slot>
    </v-main>
    <TheFooter />
  </v-app> -->
  <v-overlay v-model="viewModal">
    <v-dialog v-model="isviewModal" persistent :scrim="false" width="auto">
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img
            src="@/assets/images/view.png"
            alt="logo"
            class="img-view"
            width="100"
            height="100"
        /></v-card-title>
        <v-card-text v-html="overlayMessage"> </v-card-text>

        <div class="mr-3 mb-5 d-flex justify-end">
          <VButton
            rounded
            outlined
            color="#ffffff"
            label-color="#213E9F"
            :label="$t('buttons.close')"
            :isLarge="true"
            @click="close"
          />
        </div>
      </v-card>
    </v-dialog>
  </v-overlay>
  <v-layout>
    <TheHeadingVue />

    <TheSidebarVue />

    <v-main class="ml-20">
      <v-toolbar dark fixed app class="asguard_toolbar">
        <v-toolbar-title>
          <v-overlay v-model="loading" v-if="ztnaTab">
            <v-dialog
              v-model="isLoadingDialogue"
              :scrim="false"
              persistent
              width="auto"
            >
              <v-card color="#193286">
                <v-card-text>
                  {{ $t("requiredfield.attente") }}
                  <v-progress-linear
                    indeterminate
                    color="white"
                    class="mb-0"
                  ></v-progress-linear>
                </v-card-text>
              </v-card>
            </v-dialog>
          </v-overlay>

          <div class="d-flex">
            <label>{{ title }}</label>
            <div v-if="ztnaTab">
              <i
                v-if="!status"
                class="mdi mdi-play-circle mr-1 ml-1"
                style="color: #4caf50; font-size: 20px; cursor: pointer"
                @click="startStopServer('start')"
              ></i>
              <i
                v-if="status"
                class="mdi mdi-stop-circle"
                style="color: #b00020; font-size: 20px; cursor: pointer"
                @click="startStopServer('stop')"
              ></i>
            </div>
          </div>
        </v-toolbar-title>
        <v-spacer />
        <div v-if="back">
          <v-btn>
            {{ titleback }}
          </v-btn>
        </div>

        <v-snackbar
          :timeout="2000"
          v-model="snackbar"
          location="bottom right"
          :color="color"
        >
          {{ textAlert }}

          <template v-slot:actions> </template>
        </v-snackbar>
      </v-toolbar>
      <slot name="content"></slot>
    </v-main>

    <TheFooter />
  </v-layout>
</template>

<script>
import TheSidebarVue from "./TheSidebar.vue";
import TheHeadingVue from "./TheHeading.vue";
import TheFooter from "./TheFooter.vue";
import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";
import { user_privilege } from "@/mixins/user_privilege.js";
import VButton from "@/components/VButton.vue";

export default {
  name: "BaseLayout",
  components: {
    TheHeadingVue,
    VButton,
    TheSidebarVue,
    TheFooter,
  },
  props: {
    title: {
      type: String,
      default: "Asguard",
    },
    back: {
      type: Boolean,
      default: false,
    },
    urlback: {
      type: String,
      default: "/",
    },
    titleback: {
      type: String,
      default: "Back",
    },
    ztnaTab: {
      type: String,
    },
  },
  data() {
    return {
      isLoadingDialogue: false,
      loading: false,
      textAlert: "",
      color: "",
      snackbar: false,
      status: false,
      isviewModal: false,
      current_user: "",
      last_Subscription: [],
      viewModal: false,
    };
  },
  computed: {
    overlayMessage() {
      this.current_user = user_privilege("Ztna");
      if (this.current_user === "viewer" || this.current_user === "default") {
        return ` ${this.$t("profil.NoPermission")} <br /> ${this.$t(
          "profil.ContactAdmin"
        )}`;
      } else if (!this.last_Subscription.includes("ZTNA")) {
        return `${this.$t(
          "firewall.msg_subscription"
        )}<br /><a href="/asguard/subscription/" class="white-link"> ${this.$t(
          "firewall.sub_page"
        )}</a>`;
      } else {
        return ` ${t("profil.NoPermission")} <br /> ${t(
          "profil.ContactAdmin"
        )}`;
      }
    },
  },
  mounted() {
    this.last_Subscription = localStorage.getItem("lastSubscription");
    const csrfToken = getCookie("csrftoken");
    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

    axios.get("/ztna/status_ztna").then((response) => {
      this.status = response.data.data;
    });
  },
  methods: {
    startStopServer(status) {
      const user = user_privilege("Ztna");

      if (
        user &&
        user !== "viewer" &&
        user !== "default" &&
        this.last_Subscription.includes("ZTNA")
      ) {
        this.loading = true;
        this.isLoadingDialogue = true;
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        let endpoint = status === "start" ? "start_ztna" : "stop_ztna";
        axios
          .post(`/ztna/${endpoint}`)
          .then((response) => {
            console.log("response", response);
            this.snackbar = true;
            this.color = "success";
            this.textAlert = response.data.message;
            this.loading = false;
            this.isLoadingDialogue = false;

            setTimeout(() => {
              location.reload();
            }, 1000);
          })
          .catch((i) => {
            this.loading = false;
            this.isLoadingDialogue = false;

            if (i.response.status === 500) {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = "Internal Server Error. Please try again later";
            } else {
              this.snackbar = true;
              this.color = "red";
              this.textAlert = i.response.data.error;
            }
          });
      } else {
        this.isviewModal = true;
        this.viewModal = true;
      }
    },
    close() {
      this.isviewModal = false;
      this.viewModal = false;
    },
  },
};
</script>

<style>
/* .v-main {
  padding-top: 0px;
  left: 0;
  right: 0;
  
} */

.asguard_toolbar {
  background-color: #f8f8f8;
  color: #020202;
  font-family: OpenSans;
  font-size: 30px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  left: 0;
  right: 0;
  display: flex;
}

.white-link {
  color: white;
  text-decoration: underline;
}

.ag-paging-row-summary-panel {
  display: none;
}
</style>
