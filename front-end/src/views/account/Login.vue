<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>酒店自助入住系统</h2>
          <el-button type="text" @click="$router.push('/register')">注册</el-button>
        </div>
      </template>
      
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="loginForm.phone" placeholder="请输入手机号"></el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%;">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import axios from 'axios';

export default {
  name: 'Login',
  setup() {
    const router = useRouter();
    const loginFormRef = ref(null);
    const loading = ref(false);
    
    const loginForm = reactive({
      phone: '',
      password: ''
    });
    
    const rules = {
      phone: [
        { required: true, message: '请输入手机号', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
      ]
    };
    
    const handleLogin = async () => {
      if (!loginFormRef.value) return;
      
      await loginFormRef.value.validate(async (valid) => {
        if (valid) {
          loading.value = true;
          try {
            const response = await axios.post('http://localhost:8000/api/user/login/', {
              phone: loginForm.phone,
              password: loginForm.password
            });
            
            // 保存token和用户信息
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('user', JSON.stringify(response.data.user));
            
            ElMessage.success('登录成功');
            router.push('/dashboard');
          } catch (error) {
            console.error('登录失败:', error);
            ElMessage.error(error.response?.data?.error || '登录失败，请检查手机号和密码');
          } finally {
            loading.value = false;
          }
        }
      });
    };
    
    return {
      loginFormRef,
      loginForm,
      rules,
      loading,
      handleLogin
    };
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>