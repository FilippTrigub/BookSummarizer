import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'  // assuming you've set up vuetify

const app = createApp(App)

createApp(App)
  .use(router)
  .use(vuetify)
  .mount('#app')
