<template>
    <v-container>
        <v-row>
            <v-card class="mx-auto my-12">
                <v-card-item :style="{ backgroundColor: backgroundColor }" class="text-center white--text payment-item">
                    <v-card-title class="payment-title text-bold">{{ title }}</v-card-title>
                    <v-card-title>ASGUARD</v-card-title>
                    <v-spacer></v-spacer>
                    <div class="justify-center">
                        <div v-for="item in prices" :key="item.label"
                            style="display: flex; align-items: center; justify-content: center;">
                            <h5 class="mt-5">{{ item.amount }} € </h5>
                            <small class="mt-7"> / {{ item.label }} </small>
                        </div>
                    </div>
                </v-card-item>
                <v-card-text class="text-center mt-10 justify-center" style=" min-width: 306px; ">
                    <v-row v-for="service in communservices" :key="service" class="text-center ml-16 mb-1">
                        <v-icon color="blue" v-if="service != ''">
                            <svg width="14" height="22" viewBox="0 0 14 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M9.778 0L6.612 16.67L4.458 11.48L0 13.332L1.142 15.787L2.37 15.227L5.256 21.538H8.956L13.547 0H9.778Z"
                                    fill="#042439" />
                            </svg></v-icon>
                        <span class="ml-2">{{ service }}</span>
                    </v-row>
                    <v-row v-for="service in services" :key="service" class="text-center ml-14 mb-1" style="display: flex;">
                        <v-icon v-if="service != ''">
                            <svg width="14" height="22" viewBox="0 0 14 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M9.778 0L6.612 16.67L4.458 11.48L0 13.332L1.142 15.787L2.37 15.227L5.256 21.538H8.956L13.547 0H9.778Z"
                                    fill="#FFC300" />
                            </svg>
                        </v-icon>
                        <span class="ml-2">{{ service }}</span>
                    </v-row>
                </v-card-text>
                <v-divider class="mx-4 mb-1"></v-divider>
                <v-row>
                    <v-col cols="4"></v-col>
                    <v-col>
                        <div class="mr-3 mt-3 mb-3 text-center justify-center">
                            <VButton rounded outlined :color="buttonColor" label-color="#ffffff" label="By now"
                                :isLarge="true" class="ml-2" @click="submitForm" />
                        </div>
                    </v-col>
                    <v-col cols="4"></v-col>
                </v-row>
            </v-card>
        </v-row>
    </v-container>
</template>

<script>
import VButton from "@/components/VButton.vue";

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
        buttonColor: String,
    },
    setup(props) {
        const submitForm = () => {
            // Fonction pour soumettre le formulaire
        };

        return {
            submitForm,
        };
    },
};
</script>

<style scoped>
.payment-item {
    background-color: #213E9F;
    border-radius: 10px 10px 0 0;
    color: azure;
    width: 306px;
    height: 216.987px;
    flex-shrink: 0;
}

.payment-title {
    color: #FFF;
    font-family: Nunito;
    font-size: 20px;
    font-weight: bold;
}

.payment-title h5 {
    color: #FFF;
    font-family: Nunito;
    font-size: 30px;
    font-weight: 400;
}
</style>
