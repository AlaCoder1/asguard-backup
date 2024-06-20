<template>
  <v-app id="inspire">
    <base-layout :title="$t('subtitle.subscription')">
      <template #content>
        <v-row class="justify-center mt-5 mb-4 ml-15" v-if="subInfo">
          <v-col cols="1"> </v-col>
          <v-col cols="3">
            <v-alert
              border="start"
              color="#FFF"
              border-color="indigo accent-4"
              elevation="2"
            >
              <span class="title">{{ $t("subscription.currentPackage") }}</span>
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
              <span class="title"
                >{{ $t("subscription.currentSubscription") }} </span
              ><br />
              <span class="soutitle">{{
                statusPackage
                  ? $t("subscription.expired") +
                    "" +
                    ExpiredDays +
                    " " +
                    dayString +
                    +"" +
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
          <v-col cols="1"> </v-col>
        </v-row>
        <v-row class="mt-5">
          <v-col cols="2" />
          <v-col cols="8">
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
                :buttonColor="card.buttonColor"
              />
            </div>
          </v-col>
          <v-col cols="2" />
        </v-row>
        <br />
      </template>
    </base-layout>
  </v-app>
</template>

<script>
import { useI18n } from "vue-i18n";
import BaseLayout from "@/layouts/layout.vue";
import SubscriptionTypeCard from "./components/subscriptionTypeCard.vue";
import { onMounted, inject, ref, computed } from "vue";
import dayjs from "dayjs";
export default {
  name: "Subscription",
  components: {
    BaseLayout,
    SubscriptionTypeCard,
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
          { label: annual, amount: 1200 },
          { label: monthly, amount: 100 },
        ],
        communservices: [
          "Firewall L4",
          "Networking L2 L3",
          "VPN IPSEC",
          "LDAP",
        ],
        services: [],
        backgroundColor: "#213E9F",
        buttonColor: "#213E9F",
      },
      {
        title: custom,
        prices: [
          { label: annual, amount: 1200 },
          { label: monthly, amount: 150 },
        ],
        communservices: [
          "Firewall L4",
          "Networking L2 L3",
          "VPN IPSEC",
          "LDAP",
        ],
        services: [
          { name: "Double Masque", slug: "Double_Masque 150", price: 150, id: 1 },
          { name: "WAF", slug: "WAF 150", price: 150, id: 2 },
          { name: "IPS", slug: "IPS 100", price: 100, id: 3 },
          { name: "VPN SSL", slug: "VPN SSL 100", price: 100, id: 4 },
          { name: "Proxy", slug: "Proxy 100", price: 100, id: 5 },
          { name: "SDWAN", slug: "SDWAN 100", price: 100, id: 6 },
        ],
        backgroundColor: "#FFC300",
        buttonColor: "#FFC300",
      },
      {
        title: premium,
        prices: [
          { label: annual, amount: 1700 },
          { label: monthly, amount: 150 },
        ],
        communservices: [
          "Firewall L4",
          "Networking L2 L3",
          "VPN IPSEC",
          "LDAP",
        ],
        services: [
          { name: "Double Masque", slug: "double" },
          { name: "WAF", slug: "WAF" },
          { name: "IPS", slug: "IPS" },
          { name: "VPN SSL", slug: "VPN SSL" },
          { name: "Proxy", slug: "Proxy" },
          { name: "SDWAN", slug: "SDWAN" },
        ],
        backgroundColor: "#213E9F",
        buttonColor: "#213E9F",
      },
    ]);

    const subscriptionInfo = ref({});
    const statusPackage = ref(false);
    const ExpiredDays = ref("");
    const dayString = ref("");
    const subInfo = ref(false);

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

    onMounted(() => {
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
        let price = data + 1200;
        subscriptionCards.value[1].prices[0].amount = price;
      });
    });

    return {
      subscriptionCards,
      subscriptionInfo,
      emitter,
      formatedDate,
      formatedNextPayment,
      subInfo,
      statusPackage,
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
