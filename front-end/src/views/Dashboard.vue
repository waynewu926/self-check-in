<template>
  <el-container class="layout">
    
    <!-- 顶部栏 -->
    <el-header>
        <h2 class="system-title" @click="goToHome">智慧酒店自助入住系统</h2>

        <div class="user-info">
          <el-dropdown @command="handleCommand">
            <span>{{ userName }}</span>
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
          
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main>
        <router-view />
      </el-main>
    </el-container>

    <!-- 个人信息对话框 -->
    <el-dialog
      v-model="profileDialogVisible"
      title="个人信息"
      width="30%"
      center
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="姓名">{{ userInfo.name }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ userInfo.phone }}</el-descriptions-item>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'  // 添加axios导入

const route = useRoute()
const router = useRouter()

// 个人信息对话框控制
const profileDialogVisible = ref(false)

// 用户信息
const userName = ref('用户')
const userInfo = ref({
  name: '',
  phone: ''
})

// 获取用户信息
onMounted(() => {
  fetchUserInfo()
})

// 从后端获取用户信息
const fetchUserInfo = async () => {
  try {
    // 发送请求时包含凭证（Cookie）
    const response = await axios.get('/api/user/info/', {  
      withCredentials: true  // 关键设置：确保发送Cookie
    })
    
    if (response.data && response.data.success) {
      // 更新用户信息
      userInfo.value = response.data.data
      userName.value = response.data.data.name || '用户'
      
      // 更新本地存储（可选）
      localStorage.setItem('userInfo', JSON.stringify(response.data.data))
    } else {
      ElMessage.error('获取用户信息失败')
      checkLoginStatus()
    }
  } catch (error) {
    console.error('获取用户信息失败', error)
    
    // 如果是401错误，说明未登录或会话已过期
    if (error.response && error.response.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('userInfo')
      router.push('/login')
    } else {
      // 如果是其他错误，尝试从本地存储获取
      const userInfoStr = localStorage.getItem('userInfo')
      if (userInfoStr) {
        try {
          const parsedUserInfo = JSON.parse(userInfoStr)
          userInfo.value = parsedUserInfo
          userName.value = parsedUserInfo.name || '用户'
        } catch (error) {
          console.error('解析用户信息失败', error)
          checkLoginStatus()
        }
      } else {
        console.log('未找到用户信息')
        checkLoginStatus()
      }
    }
  }
}

// 检查登录状态
const checkLoginStatus = () => {
  // 对于Cookie/Session认证，可以发送一个轻量级请求检查登录状态
  // 或者简单地检查本地存储
  const userInfoStr = localStorage.getItem('userInfo')
  if (!userInfoStr) {
    ElMessage.warning('请先登录')
    router.push('/login')
  }
}

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})

// 点击标题返回首页
const goToHome = () => {
  router.push('/dashboard')
}

// 处理下拉菜单命令
const handleCommand = (command) => {
  if (command === 'logout') {
    // 清除登录信息
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    router.push('/login')
  } else if (command === 'profile') {
    // 显示个人信息对话框
    profileDialogVisible.value = true
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>