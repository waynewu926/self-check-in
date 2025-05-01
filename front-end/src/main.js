import { createApp } from 'vue'
import './style.css'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import axios from 'axios'
import { createPinia } from 'pinia'
import router from './router';

import App from './App.vue'

axios.defaults.withCredentials = true; // 跨域需要发送凭证（会话信息）
axios.defaults.baseURL = 'http://127.0.0.1:8000'; // 配置axios默认值

const pinia = createPinia();

const app = createApp(App);

app.use(ElementPlus)
app.use(pinia) // 挂载Pinia
app.use(router); // 挂载路由
app.mount('#app');
