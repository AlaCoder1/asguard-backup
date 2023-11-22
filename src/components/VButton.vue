<template>
  <v-btn
    rounded
    class="vbtn"
    :color="customColor"
    :large="isLarge"
    >
    <span :style="`color: ${labelColor}`">{{ label }}</span>
  </v-btn>
</template>

<script>
export default {
  props: {
    customColor: {
      type: String,
      default: "primary",
    },
    isLarge: {
      type: Boolean,
      default: false,
    },
    label: {
      type: String,
      default: "Custom Button",
    },

    labelColor: {
      type: String,
      default: "black",
    },
  },
};
</script>

<style scoped>
.vbtn {
  height: 43px;
  width: 183px;
  font-family: "Nunito-Regular", Helvetica;
  left: 0;
  letter-spacing: 0;
  line-height: normal;
  text-align: center;
  text-transform: capitalize;
}
</style>
