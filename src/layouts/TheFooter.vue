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
  display: flex;

  align-items: center;

  justify-content: center;

  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background-color: #193286;
  color: white;
  text-align: center;
  height: 47px;
  font-family: Nunito;
  font-size: 18px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
  z-index: 1000;
}
</style>
