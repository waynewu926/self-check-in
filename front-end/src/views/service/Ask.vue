<template>
 <div class="ask-container">
    <h2 class="page-title">服务请求</h2>
    
    <el-tabs v-model="activeTab" class="service-tabs">

      <el-tab-pane label="卫生服务" name="cleaning">
        <el-card class="cleaning-card">
          <el-form :model="cleaningForm" label-width="100px" :rules="cleaningRules" ref="cleaningFormRef">
            <el-form-item label="期望时间" prop="expectedTime">
              <el-time-picker
                v-model="cleaningForm.expectedTime"
                format="HH:mm"
                placeholder="选择期望服务时间"
                :disabled-hours="disabledHours"
              />
            </el-form-item>
            
            <el-form-item label="详细说明" prop="description">
              <el-input
                v-model="cleaningForm.description"
                type="textarea"
                :rows="4"
                placeholder="请详细描述您的清洁需求"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitCleaningRequest">提交请求</el-button>
              <el-button @click="resetCleaningForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 维修服务标签页 - 新增 -->
      <el-tab-pane label="维修服务" name="repair">
        <el-card class="repair-card">
          <el-form :model="repairForm" label-width="100px" :rules="repairRules" ref="repairFormRef">
            <el-form-item label="维修类型" prop="repairType">
              <el-select v-model="repairForm.repairType" placeholder="请选择维修类型">
                <el-option label="水电设施" value="plumbing" />
                <el-option label="电器设备" value="electrical" />
                <el-option label="家具设施" value="furniture" />
                <el-option label="其他问题" value="other" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="紧急程度" prop="urgency">
              <el-radio-group v-model="repairForm.urgency">
                <el-radio label="normal">一般</el-radio>
                <el-radio label="urgent">紧急</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="期望时间" prop="expectedTime">
              <el-time-picker
                v-model="repairForm.expectedTime"
                format="HH:mm"
                placeholder="选择期望服务时间"
                :disabled-hours="disabledHours"
              />
            </el-form-item>
            
            <el-form-item label="详细说明" prop="description">
              <el-input
                v-model="repairForm.description"
                type="textarea"
                :rows="4"
                placeholder="请详细描述需要维修的设施和问题"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitRepairRequest">提交请求</el-button>
              <el-button @click="resetRepairForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 服务记录标签页 -->
      <el-tab-pane label="服务记录" name="history">
        <el-card class="history-card">
          <el-empty v-if="serviceHistory.length === 0" description="暂无服务记录"></el-empty>
          
          <el-timeline v-else>
            <el-timeline-item
              v-for="(record, index) in serviceHistory"
              :key="index"
              :timestamp="record.requestTime"
              :type="getServiceStatusType(record.status)"
            >
              <el-card class="history-item-card">
                <h4>{{ getServiceTypeName(record.type) }}</h4>
                <p>状态: <el-tag :type="getServiceStatusType(record.status)">{{ getServiceStatusName(record.status) }}</el-tag></p>
                <p v-if="record.type === 'repair'">维修类型: {{ getRepairTypeName(record.repairType) }}</p>
                <p v-else>详细说明: {{ record.description }}</p>
                <p v-if="record.expectedTime">期望时间: {{ record.expectedTime }}</p>
                <p v-if="record.completedTime">完成时间: {{ record.completedTime }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 当前激活的标签页
const activeTab = ref('cleaning') // 默认显示清洁服务

// 保留卫生服务相关代码
const cleaningFormRef = ref(null)
const cleaningForm = reactive({
  expectedTime: null,
  description: ''
})

// 表单验证规则
const cleaningRules = {
  expectedTime: [
    { required: true, message: '请选择期望服务时间', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请填写详细说明', trigger: 'blur' },
    { min: 5, max: 200, message: '长度在 5 到 200 个字符', trigger: 'blur' }
  ]
}

// 维修服务相关 - 新增
const repairFormRef = ref(null)
const repairForm = reactive({
  repairType: '',
  urgency: 'normal',
  expectedTime: null,
  description: ''
})

// 维修表单验证规则
const repairRules = {
  repairType: [
    { required: true, message: '请选择维修类型', trigger: 'change' }
  ],
  urgency: [
    { required: true, message: '请选择紧急程度', trigger: 'change' }
  ],
  expectedTime: [
    { required: true, message: '请选择期望服务时间', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请填写详细说明', trigger: 'blur' },
    { min: 5, max: 200, message: '长度在 5 到 200 个字符', trigger: 'blur' }
  ]
}

// 禁用的小时（凌晨0点到早上8点）
const disabledHours = () => {
  return Array.from({ length: 8 }, (_, i) => i)
}

// 提交卫生服务请求
const submitCleaningRequest = () => {
  cleaningFormRef.value.validate((valid) => {
    if (valid) {
      // 这里应该调用API提交请求
      
      // 添加到服务记录
      serviceHistory.value.unshift({
        type: 'cleaning',
        status: 'pending',
        requestTime: new Date().toLocaleString(),
        expectedTime: cleaningForm.expectedTime ? cleaningForm.expectedTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : null,
        description: cleaningForm.description
      })
      
      ElMessage.success('清洁服务请求已提交')
      resetCleaningForm()
    } else {
      ElMessage.error('请正确填写表单')
    }
  })
}

// 提交维修服务请求 - 新增
const submitRepairRequest = () => {
  repairFormRef.value.validate((valid) => {
    if (valid) {
      // 这里应该调用API提交请求
      
      // 添加到服务记录
      serviceHistory.value.unshift({
        type: 'repair',
        repairType: repairForm.repairType,
        urgency: repairForm.urgency,
        status: 'pending',
        requestTime: new Date().toLocaleString(),
        expectedTime: repairForm.expectedTime ? repairForm.expectedTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : null,
        description: repairForm.description
      })
      
      ElMessage.success('维修服务请求已提交')
      resetRepairForm()
    } else {
      ElMessage.error('请正确填写表单')
    }
  })
}

// 重置卫生服务表单
const resetCleaningForm = () => {
  cleaningFormRef.value.resetFields()
}

// 重置维修服务表单 - 新增
const resetRepairForm = () => {
  repairFormRef.value.resetFields()
}

// 获取维修类型名称 - 新增
const getRepairTypeName = (type) => {
  const typeMap = {
    'plumbing': '水电设施',
    'electrical': '电器设备',
    'furniture': '家具设施',
    'other': '其他问题'
  }
  return typeMap[type] || type
}

// 服务记录相关
const serviceHistory = ref([
  {
    type: 'cleaning',
    status: 'completed',
    requestTime: '2023-06-01 10:00:00',
    expectedTime: '14:00',
    completedTime: '2023-06-01 14:30:00',
    description: '请帮忙清洁房间并更换床单'
  },
  {
    type: 'repair',
    repairType: 'plumbing',
    urgency: 'urgent',
    status: 'processing',
    requestTime: '2023-06-02 09:15:00',
    expectedTime: '11:00',
    description: '浴室水龙头漏水，需要维修'
  }
])

// 获取服务类型名称
const getServiceTypeName = (type) => {
  const typeMap = {
    'cleaning': '房间清洁',
    'repair': '设施维修'
  }
  return typeMap[type] || type
}

// 获取服务状态名称
const getServiceStatusName = (status) => {
  const statusMap = {
    'pending': '待处理',
    'processing': '处理中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

// 获取服务状态标签类型
const getServiceStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'processing': 'primary',
    'completed': 'success',
    'cancelled': 'info'
  }
  return typeMap[status] || ''
}
</script>

<style scoped>
.ask-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  color: #303133;
}

.service-tabs {
  margin-bottom: 20px;
}

.cleaning-card, .repair-card, .history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-item-card {
  margin-bottom: 10px;
}
</style>