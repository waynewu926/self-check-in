import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,
    isAuthenticated: false,
    isLoading: false
  }),
  
  getters: {
    // 获取用户名，如果没有则返回默认值
    userName: (state) => state.userInfo?.name || '用户',
    
    // 判断用户是否已登录
    isLoggedIn: (state) => state.isAuthenticated
  },
  
  actions: {
    // 获取用户信息
    async fetchUserInfo() {
      if (this.isLoading) return;
      
      this.isLoading = true;
      try {
        const response = await axios.get('/api/user/info/');
        if (response.data && response.data.success) {
          this.userInfo = response.data.data;
          this.isAuthenticated = true;
        } else {
          throw new Error('用户信息获取失败');
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        this.userInfo = null;
        this.isAuthenticated = false;
      } finally {
        this.isLoading = false;
      }
    },
    
    // 登录
    async login(phone, password) {
      this.isLoading = true;
      try {
        const response = await axios.post('/api/user/login/', {
          phone,
          password
        });
        
        if (response.data) {
          await this.fetchUserInfo();
          return { success: true };
        }
      } catch (error) {
        console.error('登录失败:', error);
        this.userInfo = null;
        this.isAuthenticated = false;
        
        let errorMessage = '登录失败，请检查手机号和密码';
        if (error.response?.data?.message) {
          errorMessage = error.response.data.message;
        }
        
        return { 
          success: false, 
          message: errorMessage 
        };
      } finally {
        this.isLoading = false;
      }
    },
    
    // 退出登录
    async logout() {
      this.isLoading = true;
      try {
        await axios.post('/api/user/logout/');
        this.userInfo = null;
        this.isAuthenticated = false;
        return { success: true };
      } catch (error) {
        console.error('退出登录失败:', error);
        return { 
          success: false, 
          message: '退出登录可能未完全成功' 
        };
      } finally {
        this.isLoading = false;
      }
    },
    
    // 重置状态
    resetState() {
      this.userInfo = null;
      this.isAuthenticated = false;
    }
  }
})