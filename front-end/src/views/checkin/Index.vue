<template>
  <div class="checkin-container">
    <h2 class="page-title">自助入住</h2>
    
    <!-- 步骤条 -->
    <el-steps :active="activeStep" finish-status="success" class="checkin-steps">
      <el-step title="验证预订信息" description="输入预订验证码"></el-step>
      <el-step title="确认入住" description="查看入住须知"></el-step>
      <el-step title="入住成功" description="获取房间信息"></el-step>
      <el-step title="退房" description="办理退房手续"></el-step>
    </el-steps>
    
    <!-- 步骤1: 验证码验证 -->
    <el-card v-if="activeStep === 0" class="step-card">
      <template #header>
        <div class="card-header">
          <span>请输入预订验证码</span>
        </div>
      </template>
      
      <div class="verification-content">
        <p class="verification-tip">请在线下自助机上输入您收到的4位数字验证码</p>
        
        <div class="verification-code-input">
          <el-input
            v-for="(digit, index) in verificationDigits"
            :key="index"
            v-model="verificationDigits[index]"
            maxlength="1"
            class="digit-input"
            @input="focusNextInput(index)"
            @keydown.delete="handleDelete(index)"
            ref="digitInputs"
          ></el-input>
        </div>
        
        <div class="verification-actions">
          <el-button type="primary" @click="verifyCode" :disabled="!isCodeComplete">验证</el-button>
          <el-button @click="resetCode">重置</el-button>
        </div>
        
        <div class="verification-help">
          <p>没有收到验证码？</p>
          <el-button type="text" @click="showHelpDialog">联系前台</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 步骤2: 确认入住 -->
    <el-card v-if="activeStep === 1" class="step-card">
      <template #header>
        <div class="card-header">
          <span>确认入住信息</span>
        </div>
      </template>
      
      <div class="confirm-content">
        <el-descriptions title="预订信息" :column="2" border>
          <el-descriptions-item label="预订人">{{ bookingInfo.guestName }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ maskPhone(bookingInfo.phone) }}</el-descriptions-item>
          <el-descriptions-item label="房间类型">{{ getRoomTypeName(bookingInfo.roomType) }}</el-descriptions-item>
          <el-descriptions-item label="房间号">{{ bookingInfo.roomNumber }}</el-descriptions-item>
          <el-descriptions-item label="入住日期">{{ formatDate(bookingInfo.checkInDate) }}</el-descriptions-item>
          <el-descriptions-item label="退房日期">{{ formatDate(bookingInfo.checkOutDate) }}</el-descriptions-item>
          <el-descriptions-item label="入住人数">{{ bookingInfo.guestCount }}人</el-descriptions-item>
          <el-descriptions-item label="订单号">{{ bookingInfo.orderNumber }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="confirm-notice">
          <h3>入住须知</h3>
          <ul>
            <li>请在退房当日中午12:00前办理退房手续</li>
            <li>房间内禁止吸烟，违者将收取清洁费</li>
            <li>请妥善保管您的贵重物品</li>
            <li>如需任何帮助，可点击系统中的"服务"模块</li>
          </ul>
        </div>
        
        <div class="confirm-actions">
          <el-checkbox v-model="agreedToTerms">我已阅读并同意以上入住须知</el-checkbox>
          <el-button type="primary" @click="confirmCheckin" :disabled="!agreedToTerms">确认入住</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 步骤3: 入住成功 -->
    <el-card v-if="activeStep === 2" class="step-card success-card">
      <template #header>
        <div class="card-header">
          <span>入住成功</span>
        </div>
      </template>
      
      <div class="success-content">
        <el-result
          icon="success"
          title="入住成功"
          sub-title="欢迎入住我们的酒店，祝您入住愉快！"
        >
        </el-result>
        
        <el-alert
          title="重要信息"
          type="warning"
          description="请妥善保管您的房间信息，不要泄露给他人。"
          show-icon
          :closable="false"
          class="important-alert"
        />
        
        <el-descriptions title="房间信息" :column="1" border class="room-info">
          <el-descriptions-item label="房间号">
            <span class="highlight-info">{{ bookingInfo.roomNumber }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="房间动态密码">
            <span class="highlight-info password-display">{{ roomPassword }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="密码有效期">
            <span>{{ formatDate(bookingInfo.checkInDate) }} 至 {{ formatDate(bookingInfo.checkOutDate) }}</span>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="reminder">
          <h3>温馨提示</h3>
          <p>如需任何帮助，可点击系统中的"服务"模块或拨打前台电话：<span class="highlight-info">8888</span></p>
        </div>
        
        <div class="success-actions">
          <el-button type="primary" @click="goToHome">返回首页</el-button>
          <el-button @click="goToService">前往服务</el-button>
          <el-button type="warning" @click="goToCheckout">办理退房</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 步骤4: 退房 -->
    <el-card v-if="activeStep === 3" class="step-card checkout-card">
      <template #header>
        <div class="card-header">
          <span>退房</span>
        </div>
      </template>
      
      <div class="checkout-content">
        <el-descriptions title="退房信息" :column="2" border>
          <el-descriptions-item label="预订人">{{ bookingInfo.guestName }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ maskPhone(bookingInfo.phone) }}</el-descriptions-item>
          <el-descriptions-item label="房间号">{{ bookingInfo.roomNumber }}</el-descriptions-item>
          <el-descriptions-item label="房间类型">{{ getRoomTypeName(bookingInfo.roomType) }}</el-descriptions-item>
          <el-descriptions-item label="入住日期">{{ formatDate(bookingInfo.checkInDate) }}</el-descriptions-item>
          <el-descriptions-item label="退房日期">{{ formatDate(bookingInfo.checkOutDate) }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="checkout-notice">
          <h3>退房须知</h3>
          <ul>
            <li>请确认您已结清所有消费</li>
            <li>请确认您已取走所有个人物品</li>
            <li>房卡请放在房间内或交还前台</li>
            <li>感谢您的入住，期待您的再次光临</li>
          </ul>
        </div>
        
        <div class="checkout-actions">
          <el-button type="primary" @click="confirmCheckout">确认退房</el-button>
          <el-button @click="goToHome">取消</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 退房成功对话框 -->
    <el-dialog v-model="checkoutSuccessVisible" title="退房成功" width="30%" :show-close="false">
      <div class="checkout-success">
        <el-result
          icon="success"
          title="退房成功"
          sub-title="感谢您的入住，期待您的再次光临！"
        >
        </el-result>
        
        <div class="checkout-feedback">
          <p>您对本次入住体验满意吗？</p>
          <el-rate v-model="satisfactionRate" :colors="colors"></el-rate>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="finishCheckout">完成</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 帮助对话框 -->
    <el-dialog v-model="helpDialogVisible" title="联系前台" width="30%">
      <p>如果您在自助入住过程中遇到问题，请联系前台：</p>
      <p class="contact-info">前台电话：<span class="highlight-info">8888</span></p>
      <p class="contact-info">服务热线：<span class="highlight-info">400-123-4567</span></p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="helpDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 当前步骤
const activeStep = ref(0)

// 验证码输入
const verificationDigits = ref(['', '', '', ''])
const digitInputs = ref([])

// 是否同意条款
const agreedToTerms = ref(false)

// 帮助对话框
const helpDialogVisible = ref(false)

// 验证码是否完整
const isCodeComplete = computed(() => {
  return verificationDigits.value.every(digit => digit !== '')
})

// 模拟的预订信息
const bookingInfo = reactive({
  guestName: '张三',
  phone: '13800138000',
  roomType: '1', // 豪华间
  roomNumber: '301',
  checkInDate: new Date('2023-07-15'),
  checkOutDate: new Date('2023-07-17'),
  guestCount: 2,
  orderNumber: 'R202307100001'
})

// 生成的房间密码
const roomPassword = ref('385921') // 6位数字密码

// 获取房间类型名称
const getRoomTypeName = (type) => {
  const typeMap = {
    '0': '标准间',
    '1': '豪华间',
    '2': '套房'
  }
  return typeMap[type] || type
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  if (typeof date === 'string') return date
  
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  
  return `${year}-${month}-${day}`
}

// 手机号码脱敏
const maskPhone = (phone) => {
  if (!phone || phone.length < 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 输入验证码后自动聚焦下一个输入框
const focusNextInput = (index) => {
  if (index < 3 && verificationDigits.value[index] !== '') {
    nextTick(() => {
      digitInputs.value[index + 1].focus()
    })
  }
}

// 处理删除键
const handleDelete = (index) => {
  if (verificationDigits.value[index] === '' && index > 0) {
    verificationDigits.value[index - 1] = ''
    nextTick(() => {
      digitInputs.value[index - 1].focus()
    })
  }
}

// 重置验证码
const resetCode = () => {
  verificationDigits.value = ['', '', '', '']
  nextTick(() => {
    digitInputs.value[0].focus()
  })
}

// 验证验证码
const verifyCode = () => {
  const code = verificationDigits.value.join('')
  
  // 模拟验证过程，实际应该调用API
  if (code === '1234') { // 假设正确的验证码是1234
    ElMessage.success('验证码验证成功')
    activeStep.value = 1
  } else {
    ElMessage.error('验证码错误，请重新输入')
    resetCode()
  }
}

// 显示帮助对话框
const showHelpDialog = () => {
  helpDialogVisible.value = true
}

// 确认入住
const confirmCheckin = () => {
  // 模拟确认入住过程，实际应该调用API
  ElMessage.success('确认入住成功')
  activeStep.value = 2
}

// 返回首页
const goToHome = () => {
  router.push('/dashboard')
}

// 前往服务页面
const goToService = () => {
  router.push('/dashboard/service/ask')
}

// 退房相关
const checkoutSuccessVisible = ref(false)
const satisfactionRate = ref(5)
const colors = { 3: '#E6A23C', 4: '#1989FA', 5: '#67C23A' }

// 前往退房页面
const goToCheckout = () => {
  activeStep.value = 3
}

// 确认退房
const confirmCheckout = () => {
  // 模拟退房过程，实际应该调用API
  checkoutSuccessVisible.value = true
}

// 完成退房
const finishCheckout = () => {
  checkoutSuccessVisible.value = false
  ElMessage.success('感谢您的反馈，祝您旅途愉快！')
  router.push('/dashboard')
}
</script>

<style scoped>
.checkin-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  color: #303133;
}

.checkin-steps {
  margin-bottom: 30px;
}

.step-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.verification-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.verification-tip {
  margin-bottom: 20px;
  font-size: 16px;
  color: #606266;
}

.verification-code-input {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.digit-input {
  width: 60px;
  margin: 0 10px;
  text-align: center;
}

.verification-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.verification-help {
  text-align: center;
  color: #606266;
}

.confirm-content {
  padding: 20px;
}

.confirm-notice {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.confirm-notice h3 {
  margin-top: 0;
  color: #303133;
}

.confirm-notice ul {
  padding-left: 20px;
  color: #606266;
}

.confirm-actions {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 15px;
}

.success-card {
  background-color: #f0f9eb;
}

.success-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.important-alert {
  width: 100%;
  margin: 20px 0;
}

.room-info {
  width: 100%;
  margin: 20px 0;
}

.highlight-info {
  color: #409EFF;
  font-weight: bold;
  font-size: 18px;
}

.password-display {
  letter-spacing: 5px;
  font-family: monospace;
}

.reminder {
  width: 100%;
  margin: 20px 0;
  padding: 15px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.reminder h3 {
  margin-top: 0;
  color: #E6A23C;
}

.success-actions {
  margin-top: 30px;
  display: flex;
  gap: 20px;
}

.contact-info {
  margin: 10px 0;
  font-size: 16px;
}

/* 修复输入框样式 */
:deep(.el-input__inner) {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
}

.checkout-card {
  background-color: #fdf6ec;
}

.checkout-content {
  padding: 20px;
}

.checkout-notice {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f8f8;
  border-radius: 4px;
}

.checkout-notice h3 {
  margin-top: 0;
  color: #303133;
}

.checkout-notice ul {
  padding-left: 20px;
  color: #606266;
}

.checkout-actions {
  margin-top: 30px;
  display: flex;
  gap: 20px;
}

.checkout-success {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.checkout-feedback {
  margin-top: 20px;
  text-align: center;
}
</style>