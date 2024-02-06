import { defineStore } from "pinia";
import axios from "axios";
export const useAuthStore = defineStore("auth", {
  id: "useAuthStore",
  state: () => ({
    user: null,
    isAuthenticated: false,
    csrfToken: null,
    messageStore: null,
    message:''
  }),

  actions: {
    async login(user) {
      await axios
        .post("/auth/authentification", user)
        .then((response) => {
          localStorage.setItem("user-info", JSON.stringify(response.data));

          let hrefPath = localStorage.getItem("href-path") ?? "/dashboard";
          window.location.href = hrefPath;
        })
        .catch((error) => {
          localStorage.setItem(
            "response-info",
            JSON.stringify(error.response.data)
          );
          console.log("error", error.response.data.message);
          this.message = error.response.data.message;
        });
    },

    async logout() {
      try {
        await axios.get("/auth/logout");

        this.loggedIn = false;
        this.user = null;
        window.location.href = "/";
      } catch (error) {
        console.error("Error during logout:", error);
      }
    },

    async fetchCsrfToken() {
      try {
        function getCsrfToken() {
          return new Promise((resolve) => {
            let cookieValue = null;
            if (document.cookie && document.cookie !== "") {
              const cookies = document.cookie.split(";");
              for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (
                  cookie.substring(0, "csrftoken".length + 1) === "csrftoken="
                ) {
                  cookieValue = decodeURIComponent(
                    cookie.substring("csrftoken".length + 1)
                  );
                  break;
                }
              }
            }
            resolve(cookieValue);
          });
        }
        const token = await getCsrfToken();

        this.csrfToken = token;
      } catch (error) {
        console.error("Failed to fetch CSRF token", error);
      }
    },
  },
});
