<template>
  <v-app id="inspire">
    <base-layout title="Subscription">
      <template #content>
        <v-row class="mt-5">
          <v-col cols="2" />
          <v-col cols="8">
            <h1>Choose your plan!</h1>
            <p style="font-weight: bold">
              Subscription for ASGUARD is available in three offers
            </p>
            <p class="mt-3">(Also available in hardware version)</p>
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
import BaseLayout from "@/layouts/layout.vue";
import SubscriptionTypeCard from "./components/subscriptionTypeCard.vue";
import { onMounted, inject, ref } from "vue";
export default {
  name: "Subscription",
  components: {
    BaseLayout,
    SubscriptionTypeCard,
  },
  setup() {
    const emitter = inject("emitter");
    const subscriptionCards = ref([
      {
        title: "Base",
        prices: [
          { label: "Annual", amount: 1000 },
          { label: "Monthly", amount: 100 },
        ],
        communservices: ["Firewall", "ZTNA", "LDAP"],
        services: ["", "", "", "", "", "", "", "", "", "", ""],
        backgroundColor: "#213E9F",
        buttonColor: "#213E9F",
      },
      {
        title: "Custom",
        prices: [
          { label: "Annual", amount: 1200 },
          { label: "Monthly", amount: 150 },
        ],
        communservices: ["Firewall", "ZTNA", "LDAP"],
        services: [
          "Double Mask 150 €/Annual​​",
          "CASB 150 €/Annual​",
          "SWG 100 €/Annual​",
          "Anti-virus 100 €/Annual",
        ],
        backgroundColor: "#FFC300",
        buttonColor: "#FFC300",
      },
      {
        title: "Premium",
        prices: [
          { label: "Annual", amount: 1500 },
          { label: "Monthly", amount: 150 },
        ],
        communservices: ["Firewall", "ZTNA", "LDAP"],
        services: ["Double Mask​", "CASB​", "SWG", "Anti-virus​"],
        backgroundColor: "#213E9F",
        buttonColor: "#213E9F",
      },
    ]);

    onMounted(() => {
      emitter.on("changePrice", (data) => {
        if (data > 0) {
          let price = data + 1200;
          subscriptionCards.value[1].prices[0].amount = price;
        } else if (data == 0) {
          subscriptionCards.value[1].prices[0].amount = 1000;
        }
      });
    });

    return {
      subscriptionCards,
      emitter,
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
</style>
