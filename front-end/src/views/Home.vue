<template>
  <div class="home-container">

    <h2 class="welcome-title">欢迎使用智慧酒店自助入住系统！</h2>
    
    <div class="feature-buttons">
      <router-link to="/dashboard/room/reserve" class="feature-button">
        <el-card shadow="hover">
          <el-icon class="feature-icon"><house /></el-icon>
          <div class="feature-title">客房预订</div>
          <div class="feature-desc">浏览客房、预订房间</div>
        </el-card>
      </router-link>
      
      <router-link to="/dashboard/checkin" class="feature-button">
        <el-card shadow="hover">
          <el-icon class="feature-icon"><document-checked /></el-icon>
          <div class="feature-title">自助入住</div>
          <div class="feature-desc">快速办理入住手续</div>
        </el-card>
      </router-link>
      
      <router-link to="/dashboard/service/ask" class="feature-button">
        <el-card shadow="hover">
          <el-icon class="feature-icon"><service /></el-icon>
          <div class="feature-title">服务中心</div>
          <div class="feature-desc">服务请求、反馈评价</div>
        </el-card>
      </router-link>
    </div>
    
  </div>
</template>

<script setup>
import { House, DocumentChecked, Service } from '@element-plus/icons-vue'
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.welcome-title {
  margin-top: 80px;
  margin-bottom: 120px;

  font-size: 30px;
}

.feature-buttons {
  display: flex;
  justify-content: space-between;

  max-width: 1000px;
  width: 100%;
}

.feature-button {
  width: 220px;
  height: 220px;
  text-decoration: none;

  transition: transform 0.3s;
}

.feature-button:hover {
  transform: translateY(-10px);
}

.el-card {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  
  text-align: center;
  border-radius: 8px;
}

.feature-icon {
  font-size: 50px;
  color: #409EFF;
}

.feature-title {
  margin-top: 15px;
  margin-bottom: 10px;

  font-size: 20px;
  font-weight: bold;
}

.feature-desc {
  color: #606266;
  font-size: 14px;
}
</style>