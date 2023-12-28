<template>
    <div class="cert-status-render">
      <v-chip
        color="green"
        text-color="white"
        v-if="params.data.allow_by_auth === 'Allow'"
        >{{ params.data.allow_by_auth }}</v-chip
      >
      <v-chip color="red" text-color="white" v-else>
        {{ params.data.allow_by_auth }}</v-chip
      >
    </div>
  </template>
  
  <script>
  export default {
    name: "CertAllowStatus",
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
  