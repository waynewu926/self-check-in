import { createRouter, createWebHistory } from 'vue-router';

// 定义路由配置
const routes = [
  {
    path: '/',
    redirect: '/dashboard'  // 直接重定向到仪表盘
  },
  // 删除登录和注册路由
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    // 移除认证要求
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
      // 服务模块
      {
        path: 'service',
        name: 'Service',
        children: [
          {
            path: 'ask',
            name: 'Ask',
            component: () => import('../views/service/Ask.vue')
          }, 
          {
            path: 'feedback',
            name: 'Feedback',
            component: () => import('../views/service/Feedback.vue')
          }
        ]
      }
    ]
  }
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 移除路由守卫，不再检查认证状态
// router.beforeEach((to, from, next) => {
//   const token = localStorage.getItem('token');
//   
//   if (to.matched.some(record => record.meta.requiresAuth) && !token) {
//     next({ name: 'Login' });
//   } else {
//     next();
//   }
// });

export default router;
