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
          <el-input v-model="registerForm.phone" placeholder="请输入手机号"></el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" style="width: 100%;">注册</el-button>
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
  name: 'Register',
  setup() {
    const router = useRouter();
    const registerFormRef = ref(null);
    const loading = ref(false);
    
    const registerForm = reactive({
      name: '',
      phone: '',
      password: ''
    });
    
    const rules = {
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      phone: [
        { required: true, message: '请输入手机号', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
      ]
    };
    
    const handleRegister = async () => {
      if (!registerFormRef.value) return;
      
      await registerFormRef.value.validate(async (valid) => {
        if (valid) {
          loading.value = true;
          try {
            await axios.post('http://localhost:8000/api/user/register/', {
              username: registerForm.phone,  // 使用手机号作为用户名
              name: registerForm.name,
              phone: registerForm.phone,
              password: registerForm.password
            });
            
            ElMessage.success('注册成功，请登录');
            router.push('/login');
          } catch (error) {
            console.error('注册失败:', error);
            ElMessage.error('注册失败，请稍后再试');
          } finally {
            loading.value = false;
          }
        }
      });
    };
    
    return {
      registerFormRef,
      registerForm,
      rules,
      loading,
      handleRegister
    };
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.register-card {
  width: 450px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>