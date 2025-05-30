<template>
  <el-container class="layout">
    <!-- 顶部栏 -->
    <el-header>
      <h2 class="system-title" @click="goToHome">智慧酒店自助入住系统</h2>

      <div class="user-info">
        <el-dropdown @command="handleCommand">
          <span style="color: white">{{ userStore.userName }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 侧边栏和主内容区 -->
    <el-container>
      <el-aside width="180px">
        <el-menu router :default-active="activeMenu">
          <el-sub-menu index="/dashboard/room">
            <template #title>
              <span>客房预订</span>
            </template>
            <el-menu-item index="/dashboard/room/reserve">预订客房</el-menu-item>
            <el-menu-item index="/dashboard/room/record">预订记录</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/dashboard/checkin">自助入住</el-menu-item>
          <el-sub-menu index="/dashboard/service">
            <template #title>
              <span>服务中心</span>
            </template>
            <el-menu-item index="/dashboard/service/ask">请求服务</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <el-main>
        <router-view />
      </el-main>
    </el-container>

    <!-- 个人信息对话框 -->
    <el-dialog v-model="profileDialogVisible" title="个人信息" width="30%" center>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="姓名">{{ userStore.userInfo?.name }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ userStore.userInfo?.phone }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="profileDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 状态
const profileDialogVisible = ref(false)

// 菜单激活状态
const activeMenu = computed(() => route.path)

// 标题点击跳转
const goToHome = () => router.push('/dashboard')

// 下拉菜单命令处理
const handleCommand = async (command) => {
  if (command === 'logout') {
    await handleLogout()
  } else if (command === 'profile') {
    profileDialogVisible.value = true
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    const result = await userStore.logout()
    if (result.success) {
      ElMessage.success('退出登录成功')
    } else {
      ElMessage.warning(result.message)
    }
  } finally {
    router.push('/login')
  }
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
}

.system-title:hover {
  opacity: 0.8;
}

.user-info {
  padding-right: 20px;
  cursor: pointer;
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
