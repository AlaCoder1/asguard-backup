<template>
    <v-app id="inspire">
        <base-layout title="Subscription">
            <template #content>
                <v-row class="mt-5">
                    <v-col cols="2" />
                    <v-col cols="8">
                        <h1>Shoose your plan!</h1>
                        <p>
                            Lorem ipsum dolor sit amet consectetur adipisicing elit. Quisquam
                            voluptatum, voluptatibus, quibusdam, quia voluptates voluptate
                            quos quod quas voluptatem doloribus natus. Quisquam voluptatum,
                            voluptatibus, quibusdam, quia voluptates voluptate quos quod
                            quas voluptatem doloribus natus.
                        </p>
                        <div style="display: flex; justify-content: space-between;">
                            <SubscriptionTypeCard :title="cardTitleBase" :prices="cardPrices" :services="cardServicesBase"
                                :communservices="cardServices" :backgroundColor="cardBackgroundColor"
                                :buttonColor="cardButtonColor" />
                            <SubscriptionTypeCard :title="cardTitleStandard" :prices="cardPrices"
                                :communservices="cardServices" :services="cardServicesStandard"
                                :backgroundColor="cardBackgroundColorStandard" :buttonColor="cardButtonColorStandard" />
                            <SubscriptionTypeCard :title="cardTitlePremuim" :prices="cardPricesPremuim"
                                :communservices="cardServices" :services="cardServicesPremium"
                                :backgroundColor="cardBackgroundColor" :buttonColor="cardButtonColor" />
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

export default {
    name: "Subscription",
    components: {
        BaseLayout,
        SubscriptionTypeCard
    },
    setup() {
        const cardTitleBase = "Base"
        const cardTitleStandard = "Custom"
        const cardTitlePremuim = "Premuim"
        const cardPrices = [
            { label: 'Annuel', amount: '1000' },
            { label: 'Mensuel', amount: '100' },
        ]
        const cardPricesPremuim = [
            { label: 'Annuel', amount: '1500' },
            { label: 'Mensuel', amount: '150' },
        ]
        const cardServices = ['Firewall', 'ZTNA', 'LDAP']
        const cardServicesBase = ['', '', '', '', '', '', '', '', '', '', '']
        const cardServicesStandard = ['Double Masque 150 €/ Annuel​​', 'CASB 150 €/ Annuel​', 'SWG 100 €/ Annuel​ ', 'Anti-virus​  100 €/ Annuel']
        const cardServicesPremium = ['Double Masque​', 'CASB​', 'SWG', 'Anti-virus​']
        const cardBackgroundColor = '#213E9F'
        const cardButtonColor = '#213E9F'

        const cardBackgroundColorStandard = '#FFC300'
        const cardButtonColorStandard = '#FFC300'

        return {
            cardTitleBase,
            cardTitleStandard,
            cardTitlePremuim,
            cardPrices,
            cardPricesPremuim,
            cardServices,
            cardServicesBase,
            cardServicesStandard,
            cardServicesPremium,
            cardBackgroundColor,
            cardBackgroundColorStandard,
            cardButtonColor,
            cardButtonColorStandard
        };
    },
};
</script>

<style scoped>
.text-center {
    text-align: center;
}
</style>
