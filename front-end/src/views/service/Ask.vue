<template>
  <div class="service-container">
    <h2 class="page-title">请求服务</h2>
    
    <!-- 服务请求表单 -->
    <el-card class="service-card">
      <template #header>
        <div class="card-header">
          <span>填写服务请求</span>
        </div>
      </template>
      
      <el-form :model="serviceForm" :rules="rules" ref="serviceFormRef" label-width="120px" class="service-form">
        <el-form-item label="房间号" prop="roomNumber">
          <el-select v-model="serviceForm.roomNumber" placeholder="请选择房间号" filterable>
            <el-option
              v-for="room in userRooms"
              :key="room.roomNumber"
              :label="`${room.roomNumber} (${room.roomType})`"
              :value="room.roomNumber"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="服务类型" prop="serviceType">
          <el-radio-group v-model="serviceForm.serviceType">
            <el-radio :label="1">房间清洁</el-radio>
            <el-radio :label="2">设施维修</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="紧急程度" prop="urgency">
          <el-radio-group v-model="serviceForm.urgency">
            <el-radio :label="1">普通</el-radio>
            <el-radio :label="2">优先</el-radio>
            <el-radio :label="3">紧急</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="期望服务时间" prop="expectedTime" v-if="serviceForm.serviceType === 1">
          <el-time-select
            v-model="serviceForm.expectedTime"
            start="08:00"
            step="00:30"
            end="21:00"
            placeholder="选择时间"
          />
        </el-form-item>
        
        <el-form-item label="问题描述" prop="description">
          <el-input
            v-model="serviceForm.description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述您的需求或问题..."
          />
        </el-form-item>
        
        <el-form-item label="联系电话" prop="contactPhone">
          <el-input v-model="serviceForm.contactPhone" placeholder="请输入联系电话" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitRequest" :loading="submitting">提交请求</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 服务请求历史记录 -->
    <el-card class="service-card history-card">
      <template #header>
        <div class="card-header">
          <span>服务请求历史</span>
          <el-button type="primary" size="small" @click="refreshHistory">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="serviceHistory" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="请求编号" width="100" />
        <el-table-column prop="roomNumber" label="房间号" width="100" />
        <el-table-column label="服务类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.serviceType === 1 ? 'success' : 'warning'">
              {{ getServiceTypeName(scope.row.serviceType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="紧急程度" width="120">
          <template #default="scope">
            <el-tag :type="getUrgencyType(scope.row.urgency)">
              {{ getUrgencyName(scope.row.urgency) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="问题描述" show-overflow-tooltip />
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusName(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button 
              type="danger" 
              size="small" 
              @click="cancelRequest(scope.row)"
              :disabled="scope.row.status !== 1"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="empty-data" v-if="serviceHistory.length === 0 && !loading">
        <el-empty description="暂无服务请求记录" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()

// 表单引用
const serviceFormRef = ref(null)

// 加载状态
const loading = ref(false)
const submitting = ref(false)

// 用户房间列表（假数据）
const userRooms = ref([
  { roomNumber: '101', roomType: '标准间' },
  { roomNumber: '201', roomType: '豪华间' },
  { roomNumber: '301', roomType: '套房' }
])

// 服务请求表单
const serviceForm = reactive({
  roomNumber: '',
  serviceType: 1,
  urgency: 1,
  expectedTime: '',
  description: '',
  contactPhone: userStore.userInfo?.phone || ''
})

// 表单验证规则
const rules = {
  roomNumber: [
    { required: true, message: '请选择房间号', trigger: 'change' }
  ],
  serviceType: [
    { required: true, message: '请选择服务类型', trigger: 'change' }
  ],
  urgency: [
    { required: true, message: '请选择紧急程度', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请填写问题描述', trigger: 'blur' },
    { min: 5, max: 200, message: '问题描述长度应在5到200个字符之间', trigger: 'blur' }
  ],
  contactPhone: [
    { required: true, message: '请填写联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
}

// 服务请求历史（假数据）
const serviceHistory = ref([
  {
    id: 'SR20230001',
    roomNumber: '101',
    serviceType: 1,
    urgency: 2,
    description: '请帮忙更换床单和毛巾',
    createTime: '2023-06-15 09:30:00',
    status: 2
  },
  {
    id: 'SR20230002',
    roomNumber: '201',
    serviceType: 2,
    urgency: 3,
    description: '空调不制冷，请尽快维修',
    createTime: '2023-06-16 14:20:00',
    status: 1
  }
])

// 获取服务类型名称
const getServiceTypeName = (type) => {
  const typeMap = {
    1: '房间清洁',
    2: '设施维修'
  }
  return typeMap[type] || '未知类型'
}

// 获取紧急程度名称
const getUrgencyName = (urgency) => {
  const urgencyMap = {
    1: '普通',
    2: '优先',
    3: '紧急'
  }
  return urgencyMap[urgency] || '未知'
}

// 获取紧急程度标签类型
const getUrgencyType = (urgency) => {
  const typeMap = {
    1: '',
    2: 'warning',
    3: 'danger'
  }
  return typeMap[urgency] || ''
}

// 获取状态名称
const getStatusName = (status) => {
  const statusMap = {
    1: '待处理',
    2: '处理中',
    3: '已完成',
    4: '已取消'
  }
  return statusMap[status] || '未知'
}

// 获取状态标签类型
const getStatusType = (status) => {
  const typeMap = {
    1: '',
    2: 'warning',
    3: 'success',
    4: 'info'
  }
  return typeMap[status] || ''
}

// 提交服务请求
const submitRequest = () => {
  serviceFormRef.value.validate(async (valid) => {
    if (!valid) {
      return
    }
    
    submitting.value = true
    try {
      // 模拟API请求
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 生成新的请求ID
      const newId = 'SR' + new Date().getFullYear() + String(serviceHistory.value.length + 1).padStart(4, '0')
      
      // 创建新的服务请求记录
      const newRequest = {
        id: newId,
        roomNumber: serviceForm.roomNumber,
        serviceType: serviceForm.serviceType,
        urgency: serviceForm.urgency,
        expectedTime: serviceForm.expectedTime,
        description: serviceForm.description,
        contactPhone: serviceForm.contactPhone,
        createTime: new Date().toLocaleString(),
        status: 1 // 待处理
      }
      
      // 添加到历史记录
      serviceHistory.value.unshift(newRequest)
      
      ElMessage.success('服务请求提交成功')
      resetForm()
    } catch (error) {
      console.error('提交服务请求失败:', error)
      ElMessage.error('提交失败，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}

// 重置表单
const resetForm = () => {
  serviceFormRef.value.resetFields()
}

// 刷新历史记录
const refreshHistory = async () => {
  loading.value = true
  try {
    // 模拟API请求
    await new Promise(resolve => setTimeout(resolve, 800))
    // 实际项目中这里会调用后端API获取最新数据
    ElMessage.success('刷新成功')
  } catch (error) {
    console.error('刷新历史记录失败:', error)
    ElMessage.error('刷新失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 取消服务请求
const cancelRequest = (request) => {
  ElMessageBox.confirm(
    `确定要取消服务请求 ${request.id} 吗？`,
    '取消确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      // 模拟API请求
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 更新状态
      const index = serviceHistory.value.findIndex(item => item.id === request.id)
      if (index !== -1) {
        serviceHistory.value[index].status = 4 // 已取消
      }
      
      ElMessage.success('服务请求已取消')
    } catch (error) {
      console.error('取消服务请求失败:', error)
      ElMessage.error('取消失败，请稍后重试')
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 页面加载时获取数据
onMounted(() => {
  refreshHistory()
})
</script>

<style scoped>
.service-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  color: #303133;
}

.service-card {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-form {
  max-width: 600px;
}

.history-card {
  margin-top: 30px;
}

.empty-data {
  padding: 30px 0;
}
</style>