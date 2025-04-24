<template>
  <div class="feedback-container">
    <h2 class="page-title">反馈</h2>
    
    <el-tabs v-model="activeTab" class="feedback-tabs">
      <!-- 提交反馈标签页 -->
      <el-tab-pane label="提交反馈" name="submit-feedback">
        <el-card class="feedback-form-card">
          <template #header>
            <div class="card-header">
              <span>酒店服务反馈</span>
            </div>
          </template>
          
          <el-form :model="feedbackForm" label-width="100px" :rules="feedbackRules" ref="feedbackFormRef">
            <el-form-item label="反馈类型" prop="type">
              <el-select v-model="feedbackForm.type" placeholder="请选择反馈类型">
                <el-option label="设施问题" value="facility" />
                <el-option label="服务问题" value="service" />
                <el-option label="环境问题" value="environment" />
                <el-option label="餐饮问题" value="food" />
                <el-option label="其他问题" value="other" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="问题描述" prop="description">
              <el-input
                v-model="feedbackForm.description"
                type="textarea"
                :rows="4"
                placeholder="请详细描述您遇到的问题"
              />
            </el-form-item>
            
            <el-form-item label="改进建议" prop="suggestion">
              <el-input
                v-model="feedbackForm.suggestion"
                type="textarea"
                :rows="3"
                placeholder="请提供您的改进建议（选填）"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitFeedback">提交反馈</el-button>
              <el-button @click="resetFeedbackForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 反馈记录标签页 -->
      <el-tab-pane label="反馈记录" name="feedback-history">
        <el-card class="history-card">
          <template #header>
            <div class="card-header">
              <span>我的反馈记录</span>
              <el-tag v-if="feedbackHistory.length > 0" type="info">共 {{ feedbackHistory.length }} 条记录</el-tag>
            </div>
          </template>
          
          <el-empty v-if="feedbackHistory.length === 0" description="暂无反馈记录"></el-empty>
          
          <el-timeline v-else>
            <el-timeline-item
              v-for="(record, index) in feedbackHistory"
              :key="index"
              :timestamp="record.submitTime"
              :type="getFeedbackStatusType(record.status)"
            >
              <el-card class="history-item-card">
                <div class="history-item-header">
                  <h4>{{ getFeedbackTypeName(record.type) }}</h4>
                  <el-tag :type="getFeedbackStatusType(record.status)">{{ getFeedbackStatusName(record.status) }}</el-tag>
                </div>
                <p><strong>问题描述：</strong>{{ record.description }}</p>
                <p v-if="record.suggestion"><strong>改进建议：</strong>{{ record.suggestion }}</p>
                <p v-if="record.reply"><strong>酒店回复：</strong>{{ record.reply }}</p>
                <p v-if="record.replyTime"><strong>回复时间：</strong>{{ record.replyTime }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// 当前激活的标签页
const activeTab = ref('submit-feedback')

// 反馈表单相关
const feedbackFormRef = ref(null)
const feedbackForm = reactive({
  type: '',
  description: '',
  suggestion: ''
})

// 反馈表单验证规则
const feedbackRules = {
  type: [
    { required: true, message: '请选择反馈类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请填写问题描述', trigger: 'blur' },
    { min: 5, max: 500, message: '长度在 5 到 500 个字符', trigger: 'blur' }
  ]
}

// 提交反馈
const submitFeedback = () => {
  feedbackFormRef.value.validate((valid) => {
    if (valid) {
      // 这里应该调用API提交反馈
      
      // 添加到反馈记录
      feedbackHistory.value.unshift({
        type: feedbackForm.type,
        description: feedbackForm.description,
        suggestion: feedbackForm.suggestion,
        status: 'pending',
        submitTime: new Date().toLocaleString()
      })
      
      ElMessage.success('反馈已提交，感谢您的宝贵意见')
      resetFeedbackForm()
    } else {
      ElMessage.error('请正确填写表单')
    }
  })
}

// 重置反馈表单
const resetFeedbackForm = () => {
  feedbackFormRef.value.resetFields()
}

// 反馈记录相关
const feedbackHistory = ref([
  {
    type: 'facility',
    description: '房间的空调噪音较大，影响睡眠',
    suggestion: '建议定期检修空调设备',
    status: 'replied',
    submitTime: '2023-06-01 09:30:00',
    reply: '感谢您的反馈，我们已安排工程师检修您房间的空调，并将对所有客房空调进行例行检查。',
    replyTime: '2023-06-01 11:15:00'
  },
  {
    type: 'service',
    description: '前台办理入住手续时等待时间过长',
    suggestion: '建议增加前台人员或优化入住流程',
    status: 'pending',
    submitTime: '2023-06-02 14:20:00'
  },
  {
    type: 'food',
    description: '早餐品种较少，希望能增加一些当地特色美食',
    suggestion: '可以考虑每天增加1-2种当地特色小吃',
    status: 'processing',
    submitTime: '2023-06-05 08:45:00'
  }
])

// 获取反馈类型名称
const getFeedbackTypeName = (type) => {
  const typeMap = {
    'facility': '设施问题',
    'service': '服务问题',
    'environment': '环境问题',
    'food': '餐饮问题',
    'other': '其他问题'
  }
  return typeMap[type] || type
}

// 获取反馈状态名称
const getFeedbackStatusName = (status) => {
  const statusMap = {
    'pending': '待处理',
    'processing': '处理中',
    'replied': '已回复',
    'closed': '已关闭'
  }
  return statusMap[status] || status
}

// 获取反馈状态标签类型
const getFeedbackStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'processing': 'primary',
    'replied': 'success',
    'closed': 'info'
  }
  return typeMap[status] || ''
}
</script>

<style scoped>
.feedback-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  color: #303133;
}

.feedback-tabs {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feedback-form-card, .rating-form-card, .history-card {
  margin-bottom: 20px;
}

.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.history-item-card {
  margin-bottom: 10px;
}

.rating-history-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.rating-history-item {
  margin-bottom: 10px;
}

.rating-history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rating-time {
  color: #909399;
}

.rating-details {
  margin: 15px 0;
}

.rating-detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.rating-detail-item span {
  width: 100px;
  color: #606266;
}

.rating-comment {
  margin-top: 15px;
}
</style>