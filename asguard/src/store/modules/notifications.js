import { defineStore } from "pinia";
import { ref } from "vue";

const CACHE_KEY = "asguard_notif_cache";

function loadCache() {
  try {
    return JSON.parse(localStorage.getItem(CACHE_KEY) || "{}");
  } catch {
    return {};
  }
}

export const useNotifStore = defineStore("notif", () => {
  // Initialiser depuis le cache localStorage → affichage immédiat au reload
  const cached = loadCache();
  const count = ref(cached.count ?? 0);
  const autoBackupOn = ref(cached.autoBackupOn ?? false);
  const notificationsConfigured = ref(cached.notificationsConfigured ?? false);

  function update(data) {
    count.value = (data.alerts || []).length;
    autoBackupOn.value = !!data.auto_backup_on;
    notificationsConfigured.value = !!data.notifications_configured;
    // Persist pour le prochain chargement de page
    try {
      localStorage.setItem(
        CACHE_KEY,
        JSON.stringify({
          count: count.value,
          autoBackupOn: autoBackupOn.value,
          notificationsConfigured: notificationsConfigured.value,
        })
      );
    } catch {
      // localStorage indisponible, ignorer silencieusement
    }
  }

  return { count, autoBackupOn, notificationsConfigured, update };
});
