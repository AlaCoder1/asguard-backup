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
                        <template v-if="title === 'Custom'">
                        <input type="checkbox" :id="'checkbox_' + index" :value="service" v-model="selectedServices" />
                    </template>
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
import axios from "axios";
import { ref } from "vue";

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

        const selectedServices = ref([]);
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

        const submitForm = async () => {

            const csrfToken = getCookie("csrftoken");
            axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

            const subscriptionId = getSubscriptionId();
            console.log("subscriptionId", subscriptionId);

            try {
                const response = await axios.post("/subscription/payment", {
                    "status": "true",
                    "subscription_id": subscriptionId,
                });
                if (response.ok) {
                    // Payment successful, handle the response as needed
                    console.log('Payment successful');
                } else {
                    // Handle other response statuses (e.g., errors)
                    console.error('Payment failed');
                }
            } catch (error) {
                console.log(error);
            }

        };

        const getSubscriptionId = () => {
            switch (props.title) {
                case "Base":
                    return 1;
                case "Premium":
                    return 2;
                case "Custom":
                    let selectedServicesArray = selectedServices.value;
                    console.log(selectedServicesArray);
                    if (selectedServicesArray.length === 0) {
                        return "You have to choose at least one service";
                    }
                    if (selectedServicesArray.includes('Double Mask 150 €/Annual')) {
                        if (selectedServicesArray.includes('CASB 150 €/Annual​')) {
                            if (selectedServicesArray.includes('SWG 100 €/Annual​')) {
                                if (selectedServicesArray.includes('Anti-virus 100 €/Annual')) {
                                    return 17;
                                } else {
                                    return 13;
                                }
                            } else if (selectedServicesArray.includes('Anti-virus 100 €/Annual')) {
                                return 14;
                            } else {
                                return 7;
                            }
                        } else if (selectedServicesArray.includes('SWG 100 €/Annual​')) {
                            if (selectedServicesArray.includes('Anti-virus 100 €/Annual')) {
                                return 15;
                            } else {
                                return 8;
                            }
                        } else if (selectedServicesArray.includes('Anti-virus 100 €/Annual')) {
                            return 9;
                        } else {
                            return 3;
                        }
                    } else if (selectedServicesArray.includes('CASB 150 €/Annual​')) {
                        if (selectedServicesArray.includes('SWG 100 €/Annual​')) {
                            if (selectedServicesArray.includes('Anti-virus 100 €/Annual')) {
                                return 16;
                            } else {
                                return 10;
                            }
                        } else if (selectedServicesArray.includes('Anti-virus 100 €/Annual')) {
                            return 11;
                        } else {
                            return 4;
                        }
                    } else if (selectedServicesArray.includes('SWG 100 €/Annual​')) {
                        if (selectedServicesArray.includes('Anti-virus 100 €/Annual')) {
                            return 12;
                        } else {
                            return 5;
                        }
                    } else if (selectedServicesArray.includes('Anti-virus 100 €/Annual')) {
                        return 6;
                    }
                default:
                    return 1;
            }
        };

        return {
            selectedServices,
            getCookie,
            submitForm,
            getSubscriptionId,
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
