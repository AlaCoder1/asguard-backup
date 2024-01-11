import { defineStore } from "pinia";
import axios from "axios";
export const useAuthStore = defineStore("auth", {
  id: "useAuthStore",
  state: () => ({
    user: null,
    isAuthenticated: false,
    csrfToken: null,
    messageStore: null,
  }),

  getters: {
    // isAuthenticated: (state) => !!state.user,
    // csrfToken: (state) => state.csrfToken,
  },

  actions: {
    async login(user) {
      try {
        const response = await axios.post("/auth/authentification", user);
        console.log(response.data);

        this.user = response.data;
        let userInfo = {
          username: response.data.currentUser.username,
          email: response.data.currentUser.email,
        };

        localStorage.setItem("userInfo", JSON.stringify(userInfo));
        // this.isAuthenticated = true;

        let message = "You are successfully logged in";

        this.messageStore = message;
        setTimeout(() => {
          let message = null;

          this.messageStore = message;
        }, 1000);

        let hrefPath = localStorage.getItem("href-path") ?? "/dashboard";
        window.location.href = hrefPath;
      } catch (error) {
        let message = "Invalid credentiels";

        this.messageStore = message;
        setTimeout(() => {
          let message = null;

          this.messageStore = message;
        }, 1000);
        console.error("Error during login:", error);
      }
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
