<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>智慧酒店自助入住系统</h2>
          <el-button type="text" @click="$router.push('/register')">注册</el-button>
        </div>
      </template>
      
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="loginForm.phone" placeholder="请输入手机号" maxlength="11"></el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入6位数字密码" maxlength="6" show-password></el-input>
        </el-form-item>
        
        <el-form-item class="button-container">
          <el-button type="primary" @click="handleLogin" :loading="loading">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '../../stores/user';

const router = useRouter();
const userStore = useUserStore();
const loginFormRef = ref(null);
const loading = ref(false);

const loginForm = reactive({
  phone: '',
  password: ''
});

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '密码必须为6位数字', trigger: 'blur' }
  ]
};

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        // 使用Pinia store进行登录
        const result = await userStore.login(loginForm.phone, loginForm.password);
        
        if (result.success) {
          ElMessage.success('登录成功');
          router.push('/dashboard');
        } else {
          ElMessage.error(result.message);
        }
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  /* 更浅更自然的渐变色背景 */
  background: linear-gradient(135deg, #d4f0e9 0%, #c4e0f3 100%);
  background-size: cover;
}

.login-card {
  width: 400px;
  padding: 30px;
  border-radius: 25px;
  /* 更自然的磨砂玻璃效果 */
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 调整表单内部元素样式 */
:deep(.el-form-item__label) {
  color: #333;
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.7);
  border: none;
}

/* 按钮容器样式 */
.button-container {
  display: flex;
  justify-content: center;
}

/* 修改主要按钮样式，使其更加明显 */
:deep(.el-button--primary) {
  background: linear-gradient(to right, #4a9ad1, #3d8b80);
  border: none;
  color: white;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  width: 180px; /* 设置固定宽度 */
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

/* 修改文本按钮样式 */
:deep(.el-button--text) {
  color: #4a9ad1;
  font-weight: 500;
}

:deep(.el-button--text:hover) {
  color: #3d8b80;
}
</style>