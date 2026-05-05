<template>
  <div class="backup-page">
    <h1>🔒 {{ $t('sideBar.backup') }}</h1>
    <p>Backup page - En développement...</p>
    <v-btn color="primary" @click="testClick">
      Test Button
    </v-btn>
  </div>
</template>

<script>
export default {
  name: "Backup",
  methods: {
    testClick() {
      console.log("✅ Test click works!");
      alert("Backup page is working! ✅");
    },
  },
};
</script>

<style scoped>
.backup-page {
  padding: 20px;
}
</style>