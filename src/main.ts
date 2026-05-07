import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { ElMessageBox } from 'element-plus'
import router from './router'
import './assets/styles/themes.css'
import App from './App.vue'
import CyberToast from './components/common/CyberToast.vue'
import CyberConfirm from './components/common/CyberConfirm.vue'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.component('CyberToast', CyberToast)
app.component('CyberConfirm', CyberConfirm)
app.config.globalProperties.$msgbox = ElMessageBox
app.mount('#app')
