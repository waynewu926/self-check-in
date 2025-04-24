<template>
  <el-container class="layout">
    
    <!-- 顶部栏 -->
    <el-header>
        <h2 class="system-title" @click="goToHome">智慧酒店自助入住系统</h2>

        <div class="user-info">
          <el-dropdown>
            <span>用户名</span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人信息</el-dropdown-item>
                <el-dropdown-item>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
    </el-header>
    
    <!-- 侧边栏和主内容区 -->
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="180px">
        <el-menu
          router
          :default-active="activeMenu"
          >
        
          <!-- 客房预订模块 -->
          <el-sub-menu index="/dashboard/room">
            <template #title>
              <span>客房预订</span>
            </template>
            <el-menu-item index="/dashboard/room/reserve">预订客房</el-menu-item>
            <el-menu-item index="/dashboard/room/record">预订记录</el-menu-item>
          </el-sub-menu>
          
          <!-- 自助入住模块 -->
          <el-menu-item index="/dashboard/checkin">
            <span>自助入住</span>
          </el-menu-item>
          
          <!-- 服务模块 -->
          <el-sub-menu index="/dashboard/service">
            <template #title>
              <span>服务中心</span>
            </template>
            <el-menu-item index="/dashboard/service/ask">服务请求</el-menu-item>
            <el-menu-item index="/dashboard/service/feedback">反馈</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main>
        <router-view />
      </el-main>
    </el-container>

  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})

// 点击标题返回首页
const goToHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  height: 70px;

  color: white;
  background-color: #51789e;
}

.system-title {
  cursor: pointer;
  transition: opacity 0.3s;
  margin: 0;
}

.system-title:hover {
  opacity: 0.8;
}

.user-info {
  padding-right: 20px;

  cursor: pointer;
  color: white;
}

.el-dropdown {
  color: white;
}

.el-menu {
  height: 100%;
  border-right: none;
  background-color: #b3cde3;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>