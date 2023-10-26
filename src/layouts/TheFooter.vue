<template>
  <div class="d-flex flex-column footer px-4 py-2 text-center w-100">
    Asguard 1.0 © {{ new Date().getFullYear() }} Numeryx.
  </div>
</template>

<script>
export default {
  name: "Footer",
};
</script>

<style scoped>
.footer {
  background-color: #193286;
  color: #fff;
  font-family: Nunito;
  font-size: 18px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  position: fixed;
  bottom: 0;
  width: 100%;
}
</style>
