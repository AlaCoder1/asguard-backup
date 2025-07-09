<template>
  <v-app id="inspire">
    <base-layout :title="$t('license')">
      <template #content>
        <!-- <helpModal help="subscription"  /> -->

        <div class="mb-14" v-if="loading"></div>

        <div v-else>
          <div v-if="last_Subscription.length > 0">
            <v-row class="justify-center mt-5 mb-4" v-if="subInfo">
              <v-col cols="3">
                <v-alert
                  border="start"
                  color="#FFF"
                  border-color="indigo accent-4"
                  elevation="2"
                >
                  <span class="title">{{
                    $t("subscription.currentPackage")
                  }}</span>
                  <br />
                  <span class="soutitle" style="color: #26a69a !important">{{
                    statusPackage
                      ? $t("subscription.packageExpired")
                      : subscriptionInfo.type_pack
                  }}</span>
                </v-alert>
              </v-col>
              <v-col cols="3">
                <v-alert
                  border="start"
                  color="#FFF"
                  border-color="warning accent-4"
                  elevation="2"
                >
                  <span class="title">{{
                    $t("subscription.currentSubscription")
                  }}</span
                  ><br />
                  <span class="soutitle">{{
                    getLang === "fr"
                      ? statusPackage
                        ? $t("subscription.expired") +
                          " " +
                          $t("subscription.ago") +
                          " " +
                          ExpiredDays +
                          " " +
                          dayString
                        : formatedDate
                      : statusPackage
                      ? $t("subscription.expired") +
                        " " +
                        ExpiredDays +
                        " " +
                        dayString +
                        " " +
                        $t("subscription.ago")
                      : formatedDate
                  }}</span>
                </v-alert>
              </v-col>
              <v-col cols="3">
                <v-alert
                  border="start"
                  color="#FFF"
                  border-color="success accent-4"
                  elevation="2"
                >
                  <span class="title"
                    >{{ $t("subscription.nextPaymentDue") }}
                  </span>
                  <br />
                  <span class="soutitle">{{
                    statusPackage ? "--" : formatedNextPayment
                  }}</span>
                </v-alert>
              </v-col>
            </v-row>
          </div>

          <v-container
            v-else
            fluid
            class="d-flex justify-center align-center"
            style="margin-top: 25px"
          >
            <v-card class="pa-6 elevation-12" max-width="500">
              <v-card-title class="text-h5 font-weight-bold">
                {{ $t("addlicense") }}
              </v-card-title>

              <v-card-text>
                <v-row align="center" class="mb-3">
                  <v-col cols="12">
                    <div class="text-body-2 text--secondary">
                      <v-icon small color="#213E9F" class="mr-1"
                        >mdi-information</v-icon
                      >
                      {{ $t("keylicense") }}
                    </div>
                  </v-col>
                </v-row>

                <v-text-field
                  v-model="license"
                  :label="$t('licensekey')"
                  outlined
                  prepend-inner-icon="mdi-key"
                />
              </v-card-text>

              <v-card-actions class="justify-end">
                <!-- <v-btn color="primary" dark @click="addLicense">
                <v-icon left>mdi-plus</v-icon>
                Ajouter une licence
              </v-btn> -->
                <v-btn
                  large
                  rounded
                  outlined
                  label-color="#213E9F"
                  type="submit"
                  color="indigo-darken-3"
                  :rounded="true"
                  variant="flat"
                  class="mt-3 btn-add"
                  @click="addLicense"
                >
                  <!-- <v-icon left>mdi-plus</v-icon> -->
                  <span class="text-white pr-3 pl-3">{{
                    $t("buttons.Add")
                  }}</span>
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-container>
        </div>

        <!-- <div class="d-flex text-center justify-center">
          <v-row class="mt-5" align="center" justify="start" dense>
            <v-col cols="12" sm="8" md="6" lg="4">
              <v-text-field
                v-model="license"
                label="Ajouter une licence"
                outlined
                dense
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row class="mt-5" align="center" justify="start" dense>
            <v-col cols="12" sm="4" md="2" lg="2">
              <v-btn color="primary" @click="addLicense" block> Ajouter </v-btn>
            </v-col>
          </v-row>
        </div> -->

        <!-- <v-container
          fluid
          class="d-flex justify-center align-center"
        >
          <v-card class="pa-5 mt-2 mb-7" max-width="700">
            <v-card-title class="text-h5">Ajouter une licence</v-card-title>

            <v-card-text>
              <p class="mb-4">
                La clé de licence se trouve dans l'e-mail de confirmation que
                vous avez reçu après son achat.
              </p>

              <v-text-field v-model="license" label="Clé de licence" outlined />
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="addLicense">
                AJOUTER UNE LICENCE
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-container> -->

        <!-- <v-row class="mt-5"> -->
        <!-- <v-col cols="2" /> -->
        <!-- <v-col cols="8">
            <h1 class="d-flex justify-center">
              {{ $t("subscription.chooseYourPlan") }}
            </h1>
            <div class="subscription-cards">
              <SubscriptionTypeCard
                v-for="card in subscriptionCards"
                :key="card.title"
                :title="card.title"
                :prices="card.prices"
                :communservices="card.communservices"
                :services="card.services"
                :backgroundColor="card.backgroundColor"
                :height="card.height"
                :buttonColor="card.buttonColor"
              />
            </div>
          </v-col> -->
        <!-- <v-col cols="2" /> -->
        <!-- </v-row> -->
        <br />
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import axios from "axios";
import helpModal from "@/components/modals/help.vue";
import { getCookie } from "@/mixins/csrftoken.js";
import { useI18n } from "vue-i18n";
import BaseLayout from "@/layouts/layout.vue";
// import SubscriptionTypeCard from "./components/subscriptionTypeCard.vue";
import { onMounted, inject, ref, computed } from "vue";
import { get_lang } from "@/mixins/storage_language.js";
import dayjs from "dayjs";
export default {
  name: "Subscription",
  components: {
    BaseLayout,
    // SubscriptionTypeCard,
    helpModal,
  },
  setup() {
    const { t } = useI18n();
    const emitter = inject("emitter");

    const base = computed(() => {
      return t("subscription.base");
    });
    const annual = computed(() => {
      return t("subscription.annual");
    });
    const monthly = computed(() => {
      return t("subscription.monthly");
    });
    const custom = computed(() => {
      return t("subscription.custom");
    });
    const premium = computed(() => {
      return t("subscription.premium");
    });
    const doubleMask150Annual = computed(() => {
      return t("subscription.doubleMask150Annual");
    });
    const cASB150Annual = computed(() => {
      return t("subscription.cASB150Annual");
    });
    const sWG100Annual = computed(() => {
      return t("subscription.sWG100Annual");
    });
    const antiVirus100Annual = computed(() => {
      return t("subscription.antiVirus100Annual");
    });
    const doubleMask = computed(() => {
      return t("subscription.doubleMask");
    });
    const casb = computed(() => {
      return t("subscription.casb");
    });
    const SWG = computed(() => {
      return t("subscription.SWG");
    });

    const subscriptionCards = ref([
      {
        title: base,
        prices: [
          { label: annual, amount: 999 },
          // { label: monthly, amount: 100 },
        ],
        communservices: [
          "Firewall L4",
          "Networking L2 L3",
          "VPN IPSEC",
          "LDAP",
          "Double Masque",
        ],
        services: ["", "", "", "", "", "", "", "", "", "", "", "", "", ""],
        backgroundColor: "#213E9F",
        height: "736px",
        buttonColor: "#213E9F",
      },
      {
        title: premium,
        prices: [
          { label: annual, amount: 1199 },
          // { label: monthly, amount: 150 },
        ],
        communservices: [
          "Firewall L4",
          "Networking L2 L3",
          "VPN IPSEC",
          "LDAP",
          "Double Masque",
          "IDS/IPS",
          "VPN SSL",
          "Proxy",
        ],
        services: [
          // {
          //   name: "Double Masque",
          //   slug: "Double_Masque 150",
          //   price: 150,
          //   id: 1,
          // },
          // { name: "WAF", slug: "WAF 150", price: 150, id: 2 },
          // { name: "IPS", slug: "IPS 100", price: 100, id: 3 },
          // { name: "VPN SSL", slug: "VPN SSL 100", price: 100, id: 4 },
          // { name: "Proxy", slug: "Proxy 100", price: 100, id: 5 },
          // { name: "SDWAN", slug: "SDWAN 100", price: 100, id: 6 },
        ],
        backgroundColor: "#FFC300",
        buttonColor: "#FFC300",
        height: "736px",
      },
      // {
      //   title: premium,
      //   prices: [
      //     { label: annual, amount: 1700 },
      //     { label: monthly, amount: 150 },
      //   ],
      //   communservices: [
      //     "Firewall L4",
      //     "Networking L2 L3",
      //     "VPN IPSEC",
      //     "LDAP",
      //   ],
      //   services: [
      //     { name: "Double Masque", slug: "double" },
      //     { name: "WAF", slug: "WAF" },
      //     { name: "IPS", slug: "IPS" },
      //     { name: "VPN SSL", slug: "VPN SSL" },
      //     { name: "Proxy", slug: "Proxy" },
      //     { name: "SDWAN", slug: "SDWAN" },
      //   ],
      //   backgroundColor: "#213E9F",
      //   buttonColor: "#213E9F",
      // },
    ]);

    const subscriptionInfo = ref({});
    const statusPackage = ref(false);
    const ExpiredDays = ref("");
    const getLang = ref("");
    const dayString = ref("");
    const subInfo = ref(false);
    const loading = ref(false);
    const license = ref("");
    const last_Subscription = ref([]);

    const formatedDate = computed(() => {
      if (subscriptionInfo.value.date_start && subscriptionInfo.value.end_at) {
        let from =
          dayjs(subscriptionInfo.value.date_start).format("DD, MM YYYY") ?? "";
        let to =
          dayjs(subscriptionInfo.value.end_at).format("DD, MM YYYY") ?? "";
        return `${from}  ->  ${to} `;
      }
    });
    const formatedNextPayment = computed(() => {
      if (subscriptionInfo.value.expiration_date) {
        let expire = dayjs(subscriptionInfo.value.expiration_date).format(
          "DD, MM YYYY - HH:mm"
        );

        return `${expire} `;
      }
    });

    const subscription = () => {
      loading.value = true;
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
      axios
        .get("/subscription/list_features_about_last_subscription")
        .then((response) => {
          last_Subscription.value = response.data.list_features;
          loading.value = false;
          console.log("***************0", last_Subscription.value);
        });
    };

    onMounted(() => {
      subscription();
      (async () => {
        getLang.value = await get_lang();
      })();
      const subscription_information =
        document.getElementById("app").attributes["subscription_information"]
          .value;
      let parsedArraySubscriptionInfo = JSON.parse(subscription_information);
      subscriptionInfo.value = parsedArraySubscriptionInfo;

      if (Object.keys(subscriptionInfo.value).length != 0) {
        subInfo.value = true;
        const dateLocal = new Date();
        const expireDate = new Date(subscriptionInfo.value.expiration_date);

        if (dateLocal > expireDate) {
          statusPackage.value = true;
          let Difference_In_Time = dateLocal.getTime() - expireDate.getTime();

          let Difference_In_Days = Math.round(
            Difference_In_Time / (1000 * 3600 * 24)
          );
          if (Difference_In_Days === 1) dayString.value = t("subscription.day");
          else if (Difference_In_Days > 1)
            dayString.value = t("subscription.days");
          ExpiredDays.value = Difference_In_Days;
        } else if (dateLocal < expireDate) {
          statusPackage.value = false;
          console.log("Date Start is less than Date End");
        } else {
          console.log("Date Start is equal to Date End");
        }
      } else {
        subInfo.value = false;
      }

      emitter.on("changePrice", (data) => {
        let price = data + 1199;
        subscriptionCards.value[1].prices[0].amount = price;
      });

      const allfeatures =
        document.getElementById("app").attributes["allfeature"].value;
      let all_features = JSON.parse(allfeatures);
      console.log("all_features", all_features);

      let mappedService = all_features.map((e) => {
        return {
          name: e.name,
          slug: `${e.name} ${e.price}`,
          price: e.price,
          id: e.id,
        };
      });
      subscriptionCards.value[1].services = mappedService;
    });

    const addLicense = () => {
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      if (license.value.trim() === "") {
        alert("Veuillez entrer une licence");
        return;
      } else {
        let payload = {
          key: license.value,
        };
        axios
          .post("/subscription/license_key", payload)
          .then((response) => {
            console.log("response", response);
            license.value = "";

            // state.openModal = false;
            // state.snackbar = true;
            // state.color = "success";
            // state.textAlert = response.data.msg;

            // setTimeout(() => {
            //   location.reload();
            // }, 1000);
          })
          .catch((i) => {
            // if (i.response.status === 500) {
            //   state.snackbar = true;
            //   state.color = "red";
            //   state.textAlert = t("errors.errorServer");
            // } else {
            //   state.snackbar = true;
            //   state.color = "red";
            //   state.textAlert = i.response.data.error;
            // }
          });
      }
      console.log("Licence ajoutée:", license.value);
    };

    return {
      loading,
      subscription,
      last_Subscription,
      addLicense,
      license,
      subscriptionCards,
      subscriptionInfo,
      emitter,
      formatedDate,
      formatedNextPayment,
      subInfo,
      statusPackage,
      getLang,
      ExpiredDays,
      dayString,
    };
  },
};
</script>

<style scoped>
.subscription-cards {
  display: flex;
  justify-content: space-between;
}

.text-center {
  text-align: center;
}

.title {
  color: #968e8e;
  font-size: 20px;
  font-family: "Nunito";
  font-weight: 400;
  word-wrap: break-word;
}

.soutitle {
  color: #000202;
  font-size: 18px;
  font-family: "Nunito";
  font-weight: 400;
  word-wrap: break-word;
}
</style>
