import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";

import { createVuetify } from "vuetify";

const customLightTheme = {
  colors: {
    asguard_background: "#FFFFFF",
    asguard_primary_light: "#193286",
    asguard_primary_dark: "#15202b",
    asguard_secondary: "#FFC300",
    asguard_light_grey: "#F8F8F8",
    asguard_error: "#B00020",
    asguard_success: "#4CAF50",
    asguard_warning: "#fb8c00",
  },
};

export default createVuetify({
  theme: {
    defaultTheme: "customLightTheme",
    themes: {
      customLightTheme,
    },
  },
});
