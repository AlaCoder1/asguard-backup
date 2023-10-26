import '@mdi/font/css/materialdesignicons.css'
import "vuetify/styles";

import { createVuetify } from "vuetify";

const customLightTheme = {
  dark: false,
  themes: {
    light: {
      asguard_background: "#FFFFFF",
      asguard_primary_light: "#213E9F",
      asguard_primary_dark: "#193286",
      asguard_secondary: "#FFC300",
      asguard_light_grey: "#F8F8F8",
      asguard_error: "#B00020",
      asguard_success: "#4CAF50",
      asguard_warning: "#fb8c00",
    },
  },
  colors: {
    asguard_background: "#FFFFFF",
    asguard_primary_light: "#213E9F",
    asguard_primary_dark: "#193286",
    asguard_secondary: "#FFC300",
    asguard_light_grey: "#F8F8F8",
    asguard_error: "#B00020",
    asguard_success: "#4CAF50",
    asguard_warning: "#fb8c00",
  },
  typography: {
    fontFamily: "Roboto",
    fontSize: 14,
    fontWeightLight: 300,
    fontWeightRegular: 400,
    fontWeightMedium: 500,
  },
  icons: {
    iconfont: "mdi",
  },
  breakpoint: {
    thresholds: {
      xs: 340,
      sm: 540,
      md: 800,
      lg: 1280,
    },
  },
  scrollbar: {
    minThumbSize: 20,
    thumbColor: "#FFC300",
    height: "2px",
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
