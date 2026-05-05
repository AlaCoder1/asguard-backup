import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";

const csrfToken = getCookie("csrftoken");
const api = axios.create({
  headers: {
    common: {
      "X-CSRFToken": csrfToken,
    },
  },
});

export async function checkFunctionality(
  apiUrl = "/subscription/list_features_about_last_subscription",
  redirectPath = "/asguard/license"
) {
  try {
    const response = await api.get(apiUrl);
    const last_Subscription = response.data?.list_features || [];

    if (last_Subscription.length === 0) {
      window.location.href = redirectPath;
    }
    // if (last_Subscription.length === 0) {
    //   window.location.href = redirectPath;
    // }
  } catch (error) {
    console.error(
      "Erreur lors de la vérification des fonctionnalités :",
      error
    );
    window.location.href = redirectPath;
  }
}
