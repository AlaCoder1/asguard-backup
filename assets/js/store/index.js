import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { setActivePinia, createPinia } from 'pinia'
setActivePinia(createPinia())
const store = createPinia()
store.use(piniaPluginPersistedstate)

export default store
