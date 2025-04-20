<template>
  <div class="reserve-container">
    <h2 class="page-title">预订客房</h2>
    
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" :inline="true">
        <el-form-item label="入住日期">
          <el-date-picker
            v-model="filterForm.checkInDate"
            type="date"
            placeholder="选择入住日期"
            :disabled-date="disablePastDates"
          />
        </el-form-item>
        <el-form-item label="退房日期">
          <el-date-picker
            v-model="filterForm.checkOutDate"
            type="date"
            placeholder="选择退房日期"
            :disabled-date="disableInvalidDates"
          />
        </el-form-item>
        <el-form-item label="房间类型">
          <el-select v-model="filterForm.roomType" placeholder="选择房间类型">
            <el-option label="全部" value="" />
            <el-option label="标准间" value="0" />
            <el-option label="豪华间" value="1" />
            <el-option label="套房" value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格区间">
          <el-slider
            v-model="filterForm.priceRange"
            range
            :min="100"
            :max="2000"
            :step="100"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchRooms">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 房间列表 -->
    <el-card class="room-list-card">
      <template #header>
        <div class="card-header">
          <span>可预订房间列表</span>
          <el-tag v-if="rooms.length > 0" type="success">找到 {{ rooms.length }} 个符合条件的房间</el-tag>
        </div>
      </template>
      
      <el-empty v-if="rooms.length === 0" description="暂无符合条件的房间"></el-empty>
      
      <el-table v-else :data="rooms" style="width: 100%">
        <el-table-column prop="roomNumber" label="房间号" width="100" />
        <el-table-column prop="roomType" label="房间类型" width="120">
          <template #default="scope">
            <el-tag :type="getRoomTypeTag(scope.row.roomType)">
              {{ getRoomTypeName(scope.row.roomType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格/晚" width="120">
          <template #default="scope">
            <span class="price">¥{{ scope.row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="capacity" label="可住人数" width="120" />
        <el-table-column prop="rating" label="评分" width="120">
          <template #default="scope">
            <el-rate v-model="scope.row.rating" disabled text-color="#ff9900" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="showRoomDetail(scope.row)">详情</el-button>
            <el-button type="primary" size="small" @click="selectRoom(scope.row)">预订</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 预订表单对话框 -->
    <el-dialog v-model="bookingDialogVisible" title="填写预订信息" width="50%">
      <el-form :model="bookingForm" label-width="100px" :rules="bookingRules" ref="bookingFormRef">
        <el-form-item label="入住日期">
          <el-date-picker
            v-model="bookingForm.checkInDate"
            type="date"
            placeholder="选择入住日期"
            :disabled="true"
          />
        </el-form-item>
        <el-form-item label="退房日期">
          <el-date-picker
            v-model="bookingForm.checkOutDate"
            type="date"
            placeholder="选择退房日期"
            :disabled="true"
          />
        </el-form-item>
        <el-form-item label="房间信息">
          <div class="selected-room-info">
            <span>{{ getRoomTypeName(selectedRoom.roomType) }} - {{ selectedRoom.roomNumber }}</span>
            <span class="price">¥{{ selectedRoom.price }}/晚</span>
          </div>
        </el-form-item>
        <el-divider content-position="center">入住人信息</el-divider>
        <el-form-item label="姓名" prop="guestName">
          <el-input v-model="bookingForm.guestName" placeholder="请输入入住人姓名" />
        </el-form-item>
        <el-form-item label="身份证号" prop="idCard">
          <el-input v-model="bookingForm.idCard" placeholder="请输入入住人身份证号" />
        </el-form-item>
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="bookingForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="入住人数" prop="guestCount">
          <el-input-number v-model="bookingForm.guestCount" :min="1" :max="selectedRoom.capacity" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="bookingForm.remarks" type="textarea" placeholder="如有特殊需求，请在此备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="bookingDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitBooking">提交预订</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 房间详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="房间详情" width="60%">
      <div v-if="selectedRoom.id" class="room-detail">
        <div class="room-info">
          <h3>{{ getRoomTypeName(selectedRoom.roomType) }} - {{ selectedRoom.roomNumber }}</h3>
          <div class="price-tag">¥{{ selectedRoom.price }}/晚</div>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="房间类型">{{ getRoomTypeName(selectedRoom.roomType) }}</el-descriptions-item>
            <el-descriptions-item label="可住人数">{{ selectedRoom.capacity }}人</el-descriptions-item>
            <el-descriptions-item label="床型">{{ selectedRoom.bedType }}</el-descriptions-item>
            <el-descriptions-item label="面积">{{ selectedRoom.area }}㎡</el-descriptions-item>
            <el-descriptions-item label="楼层">{{ selectedRoom.floor }}层</el-descriptions-item>
            <el-descriptions-item label="窗户">{{ selectedRoom.hasWindow ? '有窗' : '无窗' }}</el-descriptions-item>
            <el-descriptions-item label="评分">
              <el-rate v-model="selectedRoom.rating" disabled text-color="#ff9900" />
            </el-descriptions-item>
            <el-descriptions-item label="设施" :span="2">
              <el-tag v-for="facility in selectedRoom.facilities" :key="facility" size="small" class="facility-tag">
                {{ facility }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">
              {{ selectedRoom.description }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="selectRoom(selectedRoom)">预订此房间</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 验证码对话框 -->
    <el-dialog v-model="verificationDialogVisible" title="验证码确认" width="30%">
      <div class="verification-content">
        <p>验证码已发送至您的手机：{{ maskPhone(bookingForm.phone) }}</p>
        <el-input v-model="verificationCode" placeholder="请输入验证码" maxlength="4">
          <template #prefix>
            <el-icon><message /></el-icon>
          </template>
        </el-input>
        <div class="resend-code">
          <el-button type="text" :disabled="countdown > 0" @click="sendVerificationCode">
            {{ countdown > 0 ? `重新发送(${countdown}s)` : '重新发送' }}
          </el-button>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="verificationDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmBooking">确认预订</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Message } from '@element-plus/icons-vue'

// 筛选表单
const filterForm = reactive({
  checkInDate: new Date(),
  checkOutDate: new Date(Date.now() + 24 * 60 * 60 * 1000), // 默认次日
  roomType: '',
  priceRange: [300, 1000]
})

// 禁用过去的日期
const disablePastDates = (date) => {
  return date < new Date(new Date().setHours(0, 0, 0, 0))
}

// 禁用无效的退房日期（早于入住日期）
const disableInvalidDates = (date) => {
  if (!filterForm.checkInDate) return false
  return date < filterForm.checkInDate
}

// 模拟房间数据
const rooms = ref([
  {
    id: 1,
    roomNumber: '201',
    roomType: '0', // 标准间
    price: 399,
    capacity: 2,
    bedType: '双床',
    area: 25,
    floor: 2,
    hasWindow: true,
    rating: 4.5,
    facilities: ['免费WiFi', '空调', '冰箱', '电视'],
    description: '舒适标准间，配备两张单人床，适合商务出行或朋友同行。',
    images: [
      'https://example.com/room1-1.jpg',
      'https://example.com/room1-2.jpg'
    ]
  },
  {
    id: 2,
    roomNumber: '301',
    roomType: '1', // 豪华间
    price: 599,
    capacity: 2,
    bedType: '大床',
    area: 30,
    floor: 3,
    hasWindow: true,
    rating: 4.8,
    facilities: ['免费WiFi', '空调', '冰箱', '电视', '洗衣机', '烘干机'],
    description: '豪华大床房，配备一张1.8米大床，提供更宽敞的空间和更高品质的设施。',
    images: [
      'https://example.com/room2-1.jpg',
      'https://example.com/room2-2.jpg'
    ]
  },
  {
    id: 3,
    roomNumber: '501',
    roomType: '2', // 套房
    price: 899,
    capacity: 4,
    bedType: '大床+沙发床',
    area: 45,
    floor: 5,
    hasWindow: true,
    rating: 4.9,
    facilities: ['免费WiFi', '空调', '冰箱', '电视', '洗衣机', '烘干机', '客厅', '投影仪'],
    description: '豪华套房，独立客厅和卧室，提供最高级别的住宿体验。',
    images: [
      'https://example.com/room3-1.jpg',
      'https://example.com/room3-2.jpg'
    ]
  }
])

// 获取房间类型名称
const getRoomTypeName = (type) => {
  const typeMap = {
    '0': '标准间',
    '1': '豪华间',
    '2': '套房'
  }
  return typeMap[type] || type
}

// 获取房间类型标签样式
const getRoomTypeTag = (type) => {
  const tagMap = {
    '0': '',
    '1': 'success',
    '2': 'warning'
  }
  return tagMap[type] || ''
}

// 搜索房间
const searchRooms = () => {
  // 这里应该调用API获取符合条件的房间
  // 模拟API调用
  ElMessage.success('搜索成功')
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.checkInDate = new Date()
  filterForm.checkOutDate = new Date(Date.now() + 24 * 60 * 60 * 1000)
  filterForm.roomType = ''
  filterForm.priceRange = [300, 1000]
}

// 预订相关
const bookingDialogVisible = ref(false)
const selectedRoom = ref({})
const bookingFormRef = ref(null)

// 预订表单
const bookingForm = reactive({
  checkInDate: null,
  checkOutDate: null,
  guestName: '',
  idCard: '',
  phone: '',
  guestCount: 1,
  remarks: ''
})

// 表单验证规则
const bookingRules = {
  guestName: [
    { required: true, message: '请输入入住人姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  idCard: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  guestCount: [
    { required: true, message: '请选择入住人数', trigger: 'change' }
  ]
}

// 选择房间
const selectRoom = (room) => {
  selectedRoom.value = room
  bookingForm.checkInDate = filterForm.checkInDate
  bookingForm.checkOutDate = filterForm.checkOutDate
  bookingForm.guestCount = 1
  detailDialogVisible.value = false
  bookingDialogVisible.value = true
}

// 显示房间详情
const detailDialogVisible = ref(false)
const showRoomDetail = (room) => {
  selectedRoom.value = room
  detailDialogVisible.value = true
}

// 验证码相关
const verificationDialogVisible = ref(false)
const verificationCode = ref('')
const countdown = ref(0)
let countdownTimer = null

// 提交预订
const submitBooking = () => {
  bookingFormRef.value.validate((valid) => {
    if (valid) {
      sendVerificationCode()
      verificationDialogVisible.value = true
    } else {
      ElMessage.error('请正确填写预订信息')
    }
  })
}

// 发送验证码
const sendVerificationCode = () => {
  // 生成4位数字验证码
  const code = Math.floor(1000 + Math.random() * 9000)
  // 模拟发送验证码
  ElMessage.success(`验证码已发送至 ${maskPhone(bookingForm.phone)}，验证码为：${code}`)
  
  // 倒计时
  countdown.value = 60
  if (countdownTimer) clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
    }
  }, 1000)
}

// 确认预订
const confirmBooking = () => {
  if (!verificationCode.value) {
    ElMessage.warning('请输入验证码')
    return
  }
  
  // 模拟验证码验证
  ElMessageBox.alert('预订成功！您的订单号为：' + generateOrderNumber(), '预订结果', {
    confirmButtonText: '确定',
    callback: () => {
      verificationDialogVisible.value = false
      bookingDialogVisible.value = false
      resetBookingForm()
    }
  })
}

// 重置预订表单
const resetBookingForm = () => {
  bookingForm.guestName = ''
  bookingForm.idCard = ''
  bookingForm.phone = ''
  bookingForm.guestCount = 1
  bookingForm.remarks = ''
  verificationCode.value = ''
}

// 生成订单号
const generateOrderNumber = () => {
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0')
  return `R${year}${month}${day}${random}`
}

// 手机号码脱敏
const maskPhone = (phone) => {
  if (!phone || phone.length < 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 组件销毁前清除定时器
onBeforeUnmount(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
.reserve-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
}

.room-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  color: #f56c6c;
  font-weight: bold;
}

.facility-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.selected-room-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.room-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.room-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.room-info {
  padding: 10px;
}

.price-tag {
  color: #f56c6c;
  font-size: 20px;
  font-weight: bold;
  margin: 10px 0;
}

.verification-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.resend-code {
  text-align: right;
  margin-top: 5px;
}
</style>