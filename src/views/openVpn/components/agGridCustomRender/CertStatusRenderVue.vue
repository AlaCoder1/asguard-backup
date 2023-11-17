<template>
  <div class="cert-status-render">
    <v-chip color="green" text-color="white" v-if="params.data.cert_status"
      >Valid</v-chip
    >
    <v-chip color="red" text-color="white" v-else-if="params.data.cert_status">
      Revoqued</v-chip
    >
  </div>
</template>

<script>
export default {
  name: "CertStatusRenderVue",
  props: {
    params: Object,
  },
};
</script>

<style scoped>
.cert-status-render {
  margin-left: 10px;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.valid {
  color: green;
}

.expired {
  color: red;
}

.revoked {
  color: orange;
}

.unknown {
  color: gray;
}
</style>
