import { createRouter, createWebHistory } from 'vue-router';
import axios from 'axios';

// 定义路由配置
const routes = [
  {
    path: '/',
    redirect: '/login'  // 一开始默认进入到登录界面
  },
  // 登录和注册路由
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/user/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/user/Register.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }, // 需要路由守卫认证
    children: [
      {
        path: '',  // 空路径表示默认子路由
        name: 'Home',
        component: () => import('../views/Home.vue')
      },
      // 客房预订模块
      {
        path: 'room',
        name: 'Room',
        children: [
          {
            path: 'reserve',
            name: 'Reserve',
            component: () => import('../views/room/Reserve.vue')
          }, 
          {
            path: 'record',
            name: 'Record',
            component: () => import('../views/room/Record.vue')
          }
        ]
      },
      // 自助入住模块
      {
        path: 'checkin',
        name: 'Checkin',
        component: () => import('../views/checkin/Index.vue')
      },
    ]
  }
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 添加路由守卫，检查认证状态
router.beforeEach(async (to, from, next) => {
  // 如果路由不需要认证，直接放行
  if (!to.matched.some(record => record.meta.requiresAuth)) {
    next();
    return;
  }
  
  try {
    // 发送请求到后端验证用户是否已登录
    const response = await axios.get('/api/user/info/') ;
    if (response.data && response.data.success) {
      // 用户已登录，允许访问
      next();
    } else {
      // 用户未登录，重定向到登录页
      next({ name: 'Login' });
    }
  } catch (error) {
    console.error('验证登录状态失败:', error);
    // 验证失败，重定向到登录页
    next({ name: 'Login' });
  }
});

export default router;
