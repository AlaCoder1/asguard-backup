<template>
  <v-container>
    <v-row>
      <v-card class="mx-auto my-12">
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
            <span class="ml-2">{{ service }}</span>
          </v-row>
          <v-row
            v-for="service in services"
            :key="service"
            class="text-center ml-14 mb-1"
            style="display: flex"
          >
            <template v-if="title === 'Custom'">
              <input
                type="checkbox"
                :id="'checkbox_'"
                :value="service"
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
            <span class="ml-2">{{ service }}</span>
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
                label="By now"
                :isLarge="true"
                class="ml-2"
                @click="submitForm"
              />
            </div>
          </v-col>
          <v-col cols="4"></v-col>
        </v-row>
      </v-card>
    </v-row>
    <!-- <stripe-checkout ref="checkoutRef" mode="subscription" :pk="publishableKey" :line-items="lineItems"
            :success-url="successURL" :cancel-url="cancelURL" @loading="v => loading = v" /> -->
  </v-container>
</template>

<script>
import VButton from "@/components/VButton.vue";
import { ref, watch, inject } from "vue";
import axios from "axios";

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

  data() {
    return {
      publishableKey:
        "pk_test_51OVDcYKi3nwJjULPxfS2d6c6mbWGwOpsEeTADyLi8w8ZW7mMmcvcHZDYNgckyMXTnfGCER4grlGRc2KQzcK5jQJF004gmPOXWn",
      successURL: "http://localhost:8080/success",
      cancelURL: "http://localhost:8080/cancel",
      loading: false,
      lineItems: [
        {
          price: "price_1OP597BfboFCPudKhHU0RFpY",
          quantity: 1,
        },
      ],
      mode: "payment",
    };
  },
  methods: {
    // submitForm() {
    //   // You will be redirected to Stripe's secure checkout page
    //   this.$refs.checkoutRef.redirectToCheckout();
    // },
  },
  setup(props) {
    const emitter = inject("emitter");
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
      const csrfToken = getCookie("csrftoken");
      axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

      const subscriptionId = getSubscriptionId();
      if (subscriptionId === "You have to choose at least one service") {
        alert(subscriptionId);
        return;
      }
      try {
        const response = await axios.post("/auth/create_checkout_session", {
          status: "true",
          subscription_id: subscriptionId,
          price: props.prices[0].amount,
        });
        if (response.status === 200) {
          window.open(response.data.url, "_blank");
        } else {
          console.log("error");
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
                return 16;
              } else {
                return 10;
              }
            } else if (
              selectedServicesArray.includes("Anti-virus 100 €/Annual")
            ) {
              return 11;
            } else {
              return 7;
            }
          } else if (selectedServicesArray.includes("SWG 100 €/Annual​")) {
            if (selectedServicesArray.includes("Anti-virus 100 €/Annual")) {
              return 12;
            } else {
              return 5;
            }
          } else if (
            selectedServicesArray.includes("Anti-virus 100 €/Annual")
          ) {
            return 6;
          } else {
            return 4;
          }
        default:
          return "You have to choose at least one service";
      }
    };

    return {
      selectedServices,
      emitter,
      getCookie,
      getSubscriptionId,
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
</style>
