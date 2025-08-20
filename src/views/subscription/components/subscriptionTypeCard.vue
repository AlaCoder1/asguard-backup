<template>
  <v-overlay v-model="state.viewModal">
    <v-dialog
      v-model="state.isviewModal"
      persistent
      :scrim="false"
      width="auto"
    >
      <v-card color="#193286" class="alert-box">
        <v-card-title class="img-containter">
          <img
            src="@/assets/images/view.png"
            alt="logo"
            class="img-view"
            width="100"
            height="100"
        /></v-card-title>
        <v-card-text>
          {{ $t("profil.NoPermission") }}
          <br />
          {{ $t("profil.ContactAdmin") }}
        </v-card-text>

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
  <v-container>
    <v-row>
      <v-card class="mx-auto my-12" :style="{ height: height }">
        <v-card-item
          :style="{ backgroundColor: backgroundColor }"
          class="text-center white--text payment-item"
        >
          <v-card-title class="payment-title text-bold">{{
            title
          }}</v-card-title>
          <v-card-title>ASGUARD</v-card-title>
          <v-spacer></v-spacer>
          <div class="justify-center">
            <div
              v-for="item in prices"
              :key="item.label"
              style="
                display: flex;
                align-items: center;
                justify-content: center;
              "
            >
              <h5 class="mt-5">{{ item.amount }} €</h5>
              <small class="mt-7"> / {{ item.label }} </small>
            </div>
          </div>
        </v-card-item>
        <v-card-text
          class="text-center mt-10 justify-center"
          style="min-width: 306px"
        >
          <v-row
            v-for="service in communservices"
            :key="service"
            class="text-center ml-16 mb-1"
          >
            <v-icon color="blue" v-if="service != ''">
              <svg
                width="14"
                height="22"
                viewBox="0 0 14 22"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M9.778 0L6.612 16.67L4.458 11.48L0 13.332L1.142 15.787L2.37 15.227L5.256 21.538H8.956L13.547 0H9.778Z"
                  fill="#042439"
                />
              </svg>
            </v-icon>
            <!-- <span class="ml-2">{{ $t(service) }}</span> -->
            <span class="ml-2">{{ service }}</span>
          </v-row>
          <v-row
            v-for="service in services"
            :key="service"
            class="text-center ml-14 mb-1"
            style="display: flex"
          >
            <template v-if="title === 'Premium'">
              <input
                type="checkbox"
                :id="'checkbox_'"
                :value="service.slug"
                v-model="selectedServices"
              />
            </template>
            <v-icon v-if="service != ''">
              <svg
                width="14"
                height="22"
                viewBox="0 0 14 22"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M9.778 0L6.612 16.67L4.458 11.48L0 13.332L1.142 15.787L2.37 15.227L5.256 21.538H8.956L13.547 0H9.778Z"
                  fill="#FFC300"
                />
              </svg>
            </v-icon>
            <span class="ml-2">{{ service.name }}</span>
          </v-row>
        </v-card-text>
        <v-divider class="mx-4 mb-1"></v-divider>
        <v-row>
          <v-col cols="4"></v-col>
          <v-col>
            <div class="mr-3 mt-3 mb-3 text-center justify-center">
              <VButton
                rounded
                outlined
                :color="buttonColor"
                label-color="#ffffff"
                :label="$t('subscription.byNow')"
                :isLarge="true"
                class="ml-2"
                @click="submitForm"
              />
            </div>
          </v-col>
          <v-col cols="4"></v-col>
        </v-row>
      </v-card>
      <v-snackbar
        :timeout="2000"
        v-model="state.snackbar"
        location="bottom right"
        :color="state.color"
      >
        {{ state.textAlert }}
      </v-snackbar>
    </v-row>
  </v-container>
</template>

<script>
import { useI18n } from "vue-i18n";
import VButton from "@/components/VButton.vue";
import { ref, watch, inject, reactive, onMounted } from "vue";
import axios from "axios";
import { user_privilege } from "@/mixins/user_privilege.js";

export default {
  name: "SubscriptionTypeCard",
  components: {
    VButton,
  },
  props: {
    title: String,
    prices: Array,
    services: Array,
    communservices: Array,
    backgroundColor: String,
    height: String,
    buttonColor: String,
  },

  setup(props) {
    const { t } = useI18n();
    const emitter = inject("emitter");
    const selectedServices = ref([]);

    onMounted(() => {
      const allfeatures =
        document.getElementById("app").attributes["allfeature"].value;
      let all_features = JSON.parse(allfeatures);

      let mappedService = all_features.map((e) => {
        return {
          name: e.name,
          slug: `${e.name} ${e.price}`,
          price: e.price,
          id: e.id,
        };
      });
      servicesFiltred.value = mappedService;
    });

    const servicesFiltred = ref([
      // { name: "Double Masque", slug: "Double_Masque 150", price: 150, id: 1 },
      // { name: "WAF", slug: "WAF 150", price: 150, id: 2 },
      // { name: "IPS", slug: "IPS 100", price: 100, id: 3 },
      // { name: "VPN SSL", slug: "VPN SSL 100", price: 100, id: 4 },
      // { name: "Proxy", slug: "Proxy 100", price: 100, id: 5 },
      // { name: "SDWAN", slug: "SDWAN 100", price: 100, id: 6 },
    ]);

    const state = reactive({
      textAlert: "",
      color: "",
      snackbar: false,
      isviewModal: false,
      viewModal: false,
    });
    const close = () => {
      state.isviewModal = false;
      state.viewModal = false;
    };
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
    watch(
      () => selectedServices.value,
      (val) => {
        let sum = 0;

        for (let i = 0; i < val.length; i++) {
          let currentString = val[i];
          let match = currentString.match(/\d+/);

          if (match) {
            let extractedNumber = parseInt(match[0]);
            sum += extractedNumber;
          }
        }

        emitter.emit("changePrice", sum);
      }
    );

    const submitForm = async () => {
      const user = user_privilege();
      if (user !== "see_all") {
        state.isviewModal = true;
        state.viewModal = true;
      } else {
        const csrfToken = getCookie("csrftoken");
        axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

        const features = getPackId();

        // if (features.length === 4) {
        //   state.snackbar = true;
        //   state.color = "red";
        //   state.textAlert = t("subscription.chooseService");
        //   return;
        // }
        try {
          const response = await axios.post("/auth/create_checkout_session", {
            status: true,
            features: features,
            price: props.prices[0].amount,
          });
          window.open(response.data.url, "_blank");
          // location.href = response.data.url;
        } catch (error) {
          if (error.response.status === 500) {
            state.snackbar = true;
            state.color = "red";
            state.textAlert = t("errors.errorServer");
          } else {
            state.snackbar = true;
            state.color = "red";
            state.textAlert = error.response.error;
          }
        }
      }
    };

    // const getPackId = () => {
    //   if (props.title === "Base") return 1;
    //   if (props.title === "Premium") return 2;

    //   if (selectedServices.value.length === 4) {
    //     return 17;
    //   }
    //   const double = selectedServices.value.includes("double 150");
    //   if (double && selectedServices.value.length === 1) return 3;
    //   const casb = selectedServices.value.includes("casb 150");
    //   if (casb && selectedServices.value.length === 1) return 4;
    //   const swg = selectedServices.value.includes("swg 100");
    //   if (swg && selectedServices.value.length === 1) return 5;
    //   const anti = selectedServices.value.includes("anti 100");
    //   if (anti && selectedServices.value.length === 1) return 6;

    //   const dC =
    //     selectedServices.value.includes("double 150") &&
    //     selectedServices.value.includes("casb 150");

    //   if (dC && selectedServices.value.length === 2) return 7;

    //   const dS =
    //     selectedServices.value.includes("double 150") &&
    //     selectedServices.value.includes("swg 100");

    //   if (dS && selectedServices.value.length === 2) return 8;

    //   const dA =
    //     selectedServices.value.includes("double 150") &&
    //     selectedServices.value.includes("anti 100");

    //   if (dA && selectedServices.value.length === 2) return 9;

    //   const DCS =
    //     selectedServices.value.includes("double 150") &&
    //     selectedServices.value.includes("casb 150") &&
    //     selectedServices.value.includes("swg 100");

    //   if (DCS && selectedServices.value.length === 3) return 10;

    //   const DCA =
    //     selectedServices.value.includes("double 150") &&
    //     selectedServices.value.includes("casb 150") &&
    //     selectedServices.value.includes("anti 100");

    //   if (DCA && selectedServices.value.length === 3) return 11;

    //   const DSA =
    //     selectedServices.value.includes("double 150") &&
    //     selectedServices.value.includes("swg 100") &&
    //     selectedServices.value.includes("anti 100");

    //   if (DSA && selectedServices.value.length === 3) return 12;

    //   const CS =
    //     selectedServices.value.includes("casb 150") &&
    //     selectedServices.value.includes("swg 100");

    //   if (CS && selectedServices.value.length === 2) return 13;

    //   const CSA =
    //     selectedServices.value.includes("casb 150") &&
    //     selectedServices.value.includes("swg 100") &&
    //     selectedServices.value.includes("anti 100");

    //   if (CSA && selectedServices.value.length === 3) return 14;

    //   const SA =
    //     selectedServices.value.includes("swg 100") &&
    //     selectedServices.value.includes("anti 100");

    //   if (SA && selectedServices.value.length === 2) return 15;

    //   const CA =
    //     selectedServices.value.includes("casb 150") &&
    //     selectedServices.value.includes("anti 100");

    //   if (CA && selectedServices.value.length === 2) return 16;
    // };
    const getPackId = () => {
      if (props.title === "Base") return ["Basic"];
      // else  return ["Full"];
      else if (props.title === "Premium" && selectedServices.value.length) {
        let filtredService = [];

        if (selectedServices.value) {
          selectedServices.value.forEach((e) => {
            filtredService = [
              ...filtredService,
              ...servicesFiltred.value.filter((i) => i.slug === e),
            ];
          });
        }

        const sortedItems = filtredService.sort((a, b) => a.id - b.id);

        const slugs = sortedItems.map((item) => item.name);

        const communservices = [
          "Firewall L4",
          "Networking L2 L3",
          "VPN IPSEC",
          "LDAP",
          "Double Masque",
          "IDS/IPS",
          "VPN SSL",
          "Proxy",
        ];
        let combine = [...communservices, ...slugs];

        return combine;
      } else return ["Full"];
    };

    return {
      selectedServices,
      emitter,
      state,
      close,
      getCookie,
      submitForm,
    };
  },
};
</script>

<style scoped>
.payment-item {
  background-color: #213e9f;
  border-radius: 10px 10px 0 0;
  color: azure;
  width: 306px;
  height: 216.987px;
  flex-shrink: 0;
}

.payment-title {
  color: #fff;
  font-family: Nunito;
  font-size: 20px;
  font-weight: bold;
}

.payment-title h5 {
  color: #fff;
  font-family: Nunito;
  font-size: 30px;
  font-weight: 400;
}

.img-view {
  border-style: none;
  width: 100%;
  height: 250px;
  object-fit: cover;
  overflow: hidden;
}

.img-containter {
  display: flex;
  width: 100%;
  /* height: 100%; */
  padding: 0px !important;
}
</style>
<!-- let selectedServicesArray = selectedServices.value;
if (selectedServicesArray.length === 0) {
  return "You have to choose at least one service";
}
if (selectedServicesArray.includes("Double Mask 150 €/Annual")) {
  if (selectedServicesArray.includes("CASB 150 €/Annual​")) {
    if (selectedServicesArray.includes("SWG 100 €/Annual​")) {
      if (selectedServicesArray.includes("Anti-virus 100 €/Annual")) {
        return 17;
      } else {
        return 13;
      }
    } else if (
      selectedServicesArray.includes("Anti-virus 100 €/Annual")
    ) {
      return 14;
    } else {
      return 7;
    }
  } else if (selectedServicesArray.includes("SWG 100 €/Annual​")) {
    if (selectedServicesArray.includes("Anti-virus 100 €/Annual")) {
      return 15;
    } else {
      return 8;
    }
  } else if (
    selectedServicesArray.includes("Anti-virus 100 €/Annual")
  ) {
    return 9;
  }
} else if (selectedServicesArray.includes("CASB 150 €/Annual​")) {
  if (selectedServicesArray.includes("SWG 100 €/Annual​")) {
    if (selectedServicesArray.includes("Anti-virus 100 €/Annual")) {
      return 14;
      // return 16;
    } else {
      return 13;
      // return 10;
    }
  } else if (
    selectedServicesArray.includes("Anti-virus 100 €/Annual")
  ) {
    return 16;
    // return 11;
  } else {
    return 4;
    // return 7;
  }
} else if (selectedServicesArray.includes("SWG 100 €/Annual​")) {
  if (selectedServicesArray.includes("Anti-virus 100 €/Annual")) {
    return 15;
    // return 12;
  } else {
    return 8;
    // return 5;
  }
} else if (
  selectedServicesArray.includes("Anti-virus 100 €/Annual")
) {
  return 9;
  // return 6;
} else {
  return 3;
  // return 4;
} -->
