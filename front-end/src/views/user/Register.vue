<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>用户注册</h2>
          <el-button type="text" @click="$router.push('/login')">返回登录</el-button>
        </div>
      </template>
      
      <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="registerForm.name" placeholder="请输入姓名"></el-input>
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="请输入手机号" maxlength="11"></el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入6位数字密码" maxlength="6" show-password></el-input>
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" maxlength="6" show-password></el-input>
        </el-form-item>
        
        <el-form-item class="button-container">
          <el-button type="primary" @click="handleRegister" :loading="loading">注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import axios from 'axios';

const router = useRouter();
const registerFormRef = ref(null);
const loading = ref(false);

const registerForm = reactive({
  name: '',
  phone: '',
  password: '',
  confirmPassword: ''
});

// 密码一致性验证
const validatePass = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'));
  } else {
    callback();
  }
};

const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在2到20个字符之间', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '密码必须为6位数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ]
};

const handleRegister = async () => {
  if (!registerFormRef.value) return;
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        const userData = {
          name: registerForm.name,
          phone: registerForm.phone,
          password: registerForm.password,
          confirm_password: registerForm.confirmPassword
        };
        
        const response = await axios.post('/api/user/register/', userData);
        
        ElMessage.success('注册成功，请登录');
        router.push('/login');
      } catch (error) {
        console.error('注册失败:', error);
        
        // 适配Django后端的错误响应格式
        if (error.response?.data?.message) {
          ElMessage.error(error.response.data.message);
        } else if (error.response?.data) {
          if (typeof error.response.data === 'string') {
            ElMessage.error(error.response.data);
          } else {
            ElMessage.error(JSON.stringify(error.response.data));
          }
        } else {
          ElMessage.error('注册失败，请稍后再试');
        }
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  /* 更浅更自然的渐变色背景 */
  background: linear-gradient(135deg, #d4f0e9 0%, #c4e0f3 100%);
  background-size: cover;
}

.register-card {
  width: 450px;
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