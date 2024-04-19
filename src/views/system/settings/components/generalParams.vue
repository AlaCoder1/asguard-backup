<template>
  <div class="mt-3">
    <v-overlay v-model="state.loading">
      <v-dialog
        v-model="state.isLoadingDialogue"
        :scrim="false"
        persistent
        width="auto"
      >
        <v-card color="#193286">
          <v-card-text>
            Please Wait...
            <v-progress-linear
              indeterminate
              color="white"
              class="mb-0"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-overlay>
    <div class="ml-3 mr-3">
      <h4>General Parameters</h4>
      <br />

      <v-divider class="mb-2"></v-divider>
    </div>
    <v-row class="ml-3 mr-3">
      <v-col cols="6">
        <v-row class="mt-2">
          <v-col cols="8" class="mb-n6">
            <h4>System</h4>

            <v-divider class="mb-2"></v-divider>

            <v-text-field
              label="Host name"
              density="compact"
              v-model="state.hostName"
            ></v-text-field>

            <v-text-field
              label="Domain"
              density="compact"
              v-model="state.domain"
            ></v-text-field>
            <v-select
              label="Time zone"
              density="compact"
              v-model="state.timeZone"
              item-title="name"
              item-value="slug"
              return-object
              :items="state.timeZoneList"
            ></v-select>
          </v-col>
        </v-row>
        <v-row class="mt-2">
          <v-col cols="8" class="mb-n6">
            <h4>Network</h4>

            <v-divider class="mb-2"></v-divider>

            <v-card class="mt-3">
              <div class="ml-5">
                <v-row>
                  <v-col cols="12" class="d-flex justify-end">
                    <v-btn
                      color="#F6F6F6"
                      class="text-none"
                      variant="flat"
                      @click="addRow"
                    >
                      <svg
                        width="17"
                        height="17"
                        viewBox="0 0 17 17"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <mask
                          id="mask0_50_190"
                          style="mask-type: luminance"
                          maskUnits="userSpaceOnUse"
                          x="0"
                          y="0"
                          width="17"
                          height="17"
                        >
                          <path d="M17 0H0V17H17V0Z" fill="white" />
                        </mask>
                        <g mask="url(#mask0_50_190)">
                          <path
                            d="M8.70871 0.219971C10.3463 0.219971 11.9472 0.705584 13.3088 1.6154C14.6705 2.52522 15.7317 3.81838 16.3584 5.33135C16.9851 6.84432 17.1491 8.50916 16.8296 10.1153C16.5101 11.7215 15.7215 13.1968 14.5636 14.3548C13.4056 15.5128 11.9302 16.3014 10.3241 16.6209C8.7179 16.9404 7.05306 16.7764 5.54009 16.1497C4.02712 15.523 2.73396 14.4617 1.82414 13.1001C0.914324 11.7385 0.428711 10.1376 0.428711 8.49997C0.428976 6.30406 1.30142 4.19816 2.85416 2.64542C4.4069 1.09268 6.5128 0.220236 8.70871 0.219971Z"
                            fill="#086EAE"
                          />
                          <path
                            d="M13.6689 8.03597C13.7332 8.09478 13.7842 8.16654 13.8187 8.24652C13.8531 8.32651 13.8703 8.41289 13.8689 8.49997C13.8703 8.58779 13.8542 8.675 13.8216 8.75654C13.789 8.83808 13.7405 8.91233 13.6789 8.97497C13.6167 9.04086 13.5412 9.09277 13.4574 9.12725C13.3736 9.16173 13.2835 9.178 13.1929 9.17497H9.36591V12.981C9.36918 13.0709 9.35391 13.1606 9.32105 13.2443C9.28819 13.3281 9.23845 13.4042 9.17491 13.468C9.11435 13.5295 9.04187 13.578 8.96191 13.6105C8.88195 13.643 8.7962 13.6588 8.70991 13.657C8.62268 13.6583 8.53614 13.6412 8.45599 13.6068C8.37585 13.5723 8.30391 13.5212 8.24491 13.457C8.18336 13.3943 8.13487 13.3201 8.10225 13.2385C8.06963 13.157 8.05354 13.0698 8.05491 12.982V9.17697H4.22791C4.04915 9.17414 3.87848 9.10194 3.75197 8.97562C3.62546 8.84929 3.553 8.67873 3.54991 8.49997C3.54829 8.41285 3.5653 8.32639 3.59979 8.24637C3.63428 8.16635 3.68546 8.09462 3.74991 8.03597C3.81266 7.97421 3.88704 7.92552 3.96876 7.89274C4.05047 7.85995 4.13788 7.84371 4.22591 7.84497H8.05491V4.03797C8.04956 3.85273 8.11789 3.67292 8.24491 3.53797C8.30487 3.47498 8.37701 3.42483 8.45694 3.39056C8.53688 3.35629 8.62294 3.33862 8.70991 3.33862C8.79688 3.33862 8.88294 3.35629 8.96288 3.39056C9.04281 3.42483 9.11495 3.47498 9.17491 3.53797C9.3023 3.67276 9.37099 3.85259 9.36591 4.03797V7.84497H13.1929C13.2809 7.84377 13.3683 7.86003 13.45 7.89281C13.5317 7.9256 13.6061 7.97426 13.6689 8.03597Z"
                            fill="white"
                          />
                        </g>
                      </svg>
                      <span class="ml-2" style="color: #086eae">Add</span>
                    </v-btn>
                  </v-col>
                </v-row>
                <v-row class="mb-n8">
                  <v-col cols="4">DNS Server</v-col>
                  <v-col cols="4">Use the gateway</v-col>
                </v-row>
              </div>
              <v-card-item>
                <template
                  v-for="(row, index) in state.rows"
                  :key="index"
                  class="mt-0"
                >
                  <v-row class="mt-3">
                    <v-col cols="5" class="mb-n6">
                      <v-text-field
                        label="DNS server"
                        density="compact"
                        v-model="row.dns_server"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="5" class="mb-n6">
                      <v-text-field
                        label="Gateway"
                        density="compact"
                        v-model="row.gateway"
                      ></v-text-field>
                    </v-col>
                    <v-col
                      :cols="index !== 0 ? '2' : '0'"
                      class="mt-4"
                      v-if="index !== 0"
                    >
                      <v-icon
                        color="red"
                        @click="removeRow(index)"
                        icon="mdi mdi-delete-circle"
                      ></v-icon>
                    </v-col>
                  </v-row>
                </template>
              </v-card-item>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <v-row class="flex py-8 mb-5">
      <v-col cols="4"> </v-col>
      <v-col>
        <div class="mr-3 flex center">
          <VButton
            rounded
            outlined
            color="#213E9F"
            label-color="#ffffff"
            label="save"
            :isLarge="true"
            class="ml-2"
            @click="submitForm"
          />
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import axios from "axios";
import VButton from "@/components/VButton.vue";
import { reactive, onMounted, computed, ref, inject } from "vue";

export default {
  name: "ConfigurationComponent",
  components: {
    VButton,
  },

  setup() {
    const emitter = inject("emitter");
    const state = reactive({
      timeZoneList: [],

      rows: [
        { dns_server: "", gateway: "" },
        { dns_server: "", gateway: "" },
      ],
      //
      loading: false,
      isLoadingDialogue: false,

      snackbar: false,
      color: "",
      textAlert: "",
      //General params
      timeZone: "",
      domain: "",
      hostName: "",
    });

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

    const addRow = () => {
      state.rows.push({
        dns_server: "",
        gateway: "",
      });
    };
    const removeRow = (index) => {
      state.rows.splice(index, 1);
    };

    onMounted(async () => {});

    const submitForm = async () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (!rowDataAF.value) {
        rowDataAF.value = [];
      }

      //   if (rowDataAF.value.length) {
      //     var mapedRow = rowDataAF.value.map((e) => {
      //       let filtredCopy = state.mapedInterface
      //         .filter((i) => i.name === e.copy_iface)
      //         .map((i) => {
      //           return {
      //             id: i.id,
      //             name: i.ifname,
      //           };
      //         });

      //       return {
      //         id: e.id ?? e.id_interface,
      //         interface: e.ifname,
      //         threads: e.threads,
      //         cluster_id: e.cluster_id,
      //         cluster_type: e.cluster_type,
      //         defrag: e.defrag,
      //         use_mmap: e.use_mmap,
      //         ring_size: e.ring_size,
      //         copy_iface: filtredCopy[0] ?? null,
      //         copy_mode: e.copy_mode === "--" ? null : e.copy_mode,
      //       };
      //     });

      //     let payload = {
      //       status_enabled: state.status_enabled,
      //       promisc: state.promisc,
      //       eve_log: state.eve_log,
      //       syslog: state.syslog,
      //       mpm_algo: state.mpm_algo.slug,
      //       profile: state.profile.slug,
      //       mode_inline: state.mode_inline,
      //       list_interfaces: mapedRow,
      //     };
      //     state.loading = true;
      //     state.isLoadingDialogue = true;
      //     axios
      //       .put("/ids-ips/UpdateGeneralConfig/" + state.interId, payload)
      //       .then((response) => {
      //         if (response.status == 200) {
      //           state.loading = false;
      //           state.isLoadingDialogue = false;
      //           state.snackbar = true;
      //           state.color = "success";
      //           state.textAlert = "Configuration saved successfully!";
      //           // Automatically close the snackbar after 3000 milliseconds (3 seconds)
      //           setTimeout(() => {
      //             state.snackbar = false;
      //             location.reload();
      //           }, 1000);
      //         } else {
      //           state.loading = false;
      //           state.isLoadingDialogue = false;
      //           state.snackbar = true;
      //           state.color = "error";
      //           state.textAlert = "Failed to save configuration!";
      //           // Automatically close the snackbar after 3000 milliseconds (3 seconds)
      //           setTimeout(() => {
      //             state.snackbar = false;
      //             location.reload();
      //           }, 1000);
      //         }
      //       })
      //       .catch((i) => {
      //         state.loading = false;
      //         state.isLoadingDialogue = false;
      //         state.snackbar = true;
      //         state.color = "error";
      //         state.textAlert = error;
      //         setTimeout(() => {
      //           state.snackbar = false;
      //           location.reload();
      //         }, 1000);
      //       });
      //   } else {
      //     state.snackbar = true;
      //     state.color = "error";
      //     state.textAlert = "Minimum One Interface In AF Packet";
      //     setTimeout(() => {
      //       state.snackbar = false;
      //     }, 2000);
      //   }
    };
    const cancel = () => {};

    return {
      cancel,
      getCookie,
      submitForm,
      state,
      emitter,
      removeRow,
      addRow,
    };
  },
};
</script>
<style lang="scss">
.error-feedback {
  color: orange;
  font-size: 0.85em;
}

.label-style {
  color: #020202;
  font-family: Nunito;
  font-size: 15px;
  font-style: normal;
  font-weight: 300;
  line-height: normal;
}
/* CSS to style the text */
.text-xs {
  font-size: 12px; /* Example font size for small text */
}
.container {
  height: 50px;
}
</style>
