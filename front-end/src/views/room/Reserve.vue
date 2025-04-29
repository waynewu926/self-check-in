<template>
  <div class="reserve-container">
    <h2 class="page-title">客房预订</h2>
    
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" :inline="true">
        <el-form-item label="入住日期">
          <el-date-picker
            v-model="filterForm.checkInDate"
            type="date"
            placeholder="选择入住日期"
            :disabled-date="disablePastDates"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item label="退房日期">
          <el-date-picker
            v-model="filterForm.checkOutDate"
            type="date"
            placeholder="选择退房日期"
            :disabled-date="disableInvalidDates"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item label="房型">
          <el-select v-model="filterForm.roomType" placeholder="选择房型" clearable>
            <el-option label="全部" value="" />
            <el-option label="标准间" value="1" />
            <el-option label="豪华间" value="2" />
            <el-option label="套房" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchRooms">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 可用房间列表 -->
    <el-card class="room-list-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>可用房间列表</span>
        </div>
      </template>
      
      <el-empty v-if="availableRooms.length === 0" description="暂无可用房间"></el-empty>
      
      <div v-else class="room-list">
        <el-card v-for="room in availableRooms" :key="room.id" class="room-card">
          <div class="room-info">
            <div class="room-header">
              <h3>{{ getRoomTypeName(room.room_type) }} - {{ room.room_number }}</h3>
              <span class="room-price">¥{{ room.price }}/晚</span>
            </div>
            <div class="room-tags">
              <el-tag v-for="(facility, index) in getRoomFacilities(room.room_type)" :key="index" size="small">
                {{ facility }}
              </el-tag>
            </div>
            <div class="room-actions">
              <el-button type="primary" size="small" @click="showRoomDetail(room)">详情</el-button>
              <el-button type="success" size="small" @click="showBookingForm(room)">预订</el-button>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 房间详情对话框 -->
    <el-dialog v-model="detailDialogVisible" :title="selectedRoom.room_type ? `${getRoomTypeName(selectedRoom.room_type)} 详情` : '房间详情'" width="60%">
      <div v-if="selectedRoom.id" class="room-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="房间号">{{ selectedRoom.room_number }}</el-descriptions-item>
          <el-descriptions-item label="房型">{{ getRoomTypeName(selectedRoom.room_type) }}</el-descriptions-item>
          <el-descriptions-item label="价格">¥{{ selectedRoom.price }}/晚</el-descriptions-item>
          <el-descriptions-item label="设施">
            <div class="facility-list">
              <el-tag v-for="(facility, index) in getRoomFacilities(selectedRoom.room_type)" :key="index" class="facility-tag">
                {{ facility }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="详细描述">
            {{ getRoomDescription(selectedRoom.room_type) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="showBookingForm(selectedRoom)">预订此房间</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 预订表单对话框 -->
    <el-dialog v-model="bookingDialogVisible" title="填写预订信息" width="50%">
      <el-form :model="bookingForm" :rules="bookingRules" ref="bookingFormRef" label-width="100px">
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
          <span>{{ getRoomTypeName(bookingForm.roomType) }} - {{ bookingForm.roomNumber }}</span>
        </el-form-item>
        <el-form-item label="入住天数">
          <span>{{ calculateDays(bookingForm.checkInDate, bookingForm.checkOutDate) }}天</span>
        </el-form-item>
        <el-form-item label="总价">
          <span class="total-price">¥{{ calculateTotalPrice() }}</span>
        </el-form-item>
        <el-form-item label="入住人姓名" prop="guestName">
          <el-input v-model="bookingForm.guestName" placeholder="请输入入住人姓名"></el-input>
        </el-form-item>
        <el-form-item label="联系电话" prop="guestPhone">
          <el-input v-model="bookingForm.guestPhone" placeholder="请输入联系电话"></el-input>
        </el-form-item>
        <el-form-item label="身份证号" prop="guestIdCard">
          <el-input v-model="bookingForm.guestIdCard" placeholder="请输入身份证号"></el-input>
        </el-form-item>
        <el-form-item label="入住人数" prop="guestCount">
          <el-input-number v-model="bookingForm.guestCount" :min="1" :max="4"></el-input-number>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="bookingDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitBooking">提交预订</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 验证码确认对话框 -->
    <el-dialog v-model="codeDialogVisible" title="预订成功" width="30%">
      <div class="code-info">
        <p>您的预订已成功提交！</p>
        <p>订单号: <span class="highlight">{{ bookingResult.booking_number }}</span></p>
        <p>验证码: <span class="highlight">{{ bookingResult.code }}</span></p>
        <p class="code-tip">请妥善保管您的验证码，入住时需要使用。</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="finishBooking">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 筛选表单
const filterForm = reactive({
  checkInDate: null,
  checkOutDate: null,
  roomType: ''
})

// 可用房间列表
const availableRooms = ref([])
const loading = ref(false)

// 详情对话框
const detailDialogVisible = ref(false)
const selectedRoom = ref({})

// 预订表单对话框
const bookingDialogVisible = ref(false)
const bookingFormRef = ref(null)
const bookingForm = reactive({
  roomId: '',
  roomNumber: '',
  roomType: '',
  checkInDate: null,
  checkOutDate: null,
  guestName: '',
  guestPhone: '',
  guestIdCard: '',
  guestCount: 1
})

// 验证码对话框
const codeDialogVisible = ref(false)
const bookingResult = ref({})

// 表单验证规则
const bookingRules = {
  guestName: [
    { required: true, message: '请输入入住人姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  guestPhone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  guestIdCard: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号码', trigger: 'blur' }
  ],
  guestCount: [
    { required: true, message: '请输入入住人数', trigger: 'blur' },
    { type: 'number', min: 1, max: 4, message: '入住人数在 1 到 4 人之间', trigger: 'blur' }
  ]
}

// 禁用过去的日期
const disablePastDates = (date) => {
  return date < new Date(new Date().setHours(0, 0, 0, 0))
}

// 禁用无效的退房日期（早于入住日期）
const disableInvalidDates = (date) => {
  if (!filterForm.checkInDate) return disablePastDates(date)
  return date <= filterForm.checkInDate
}

// 处理日期变化
const handleDateChange = () => {
  if (filterForm.checkInDate && filterForm.checkOutDate) {
    if (filterForm.checkOutDate <= filterForm.checkInDate) {
      // 如果退房日期早于或等于入住日期，自动调整为入住日期后一天
      const nextDay = new Date(filterForm.checkInDate)
      nextDay.setDate(nextDay.getDate() + 1)
      filterForm.checkOutDate = nextDay
    }
  }
}

// 获取房型名称
const getRoomTypeName = (type) => {
  const typeMap = {
    '1': '标准间',
    '2': '豪华间',
    '3': '套房'
  }
  return typeMap[type] || type
}

// 获取房间设施
const getRoomFacilities = (type) => {
  const facilitiesMap = {
    '1': ['免费WiFi', '空调', '冰箱', '电视'],
    '2': ['免费WiFi', '空调', '冰箱', '电视', '洗衣机', '烘干机'],
    '3': ['免费WiFi', '空调', '冰箱', '电视', '洗衣机', '烘干机', '客厅', '投影仪']
  }
  return facilitiesMap[type] || []
}

// 获取房间描述
const getRoomDescription = (type) => {
  const descriptionMap = {
    '1': '标准间配备基本舒适设施，适合商务出行或短期休闲旅行。房间干净整洁，提供免费WiFi、空调、冰箱和电视等基本设施，满足您的日常需求。',
    '2': '豪华间提供更加舒适的住宿体验，除了标准间的所有设施外，还配备了洗衣机和烘干机，让您的长期住宿更加便利。房间宽敞明亮，装修精美，为您提供高品质的住宿体验。',
    '3': '套房是我们酒店的高端住宿选择，拥有独立的客厅和卧室，配备齐全的设施，包括投影仪等娱乐设备。宽敞的空间和豪华的装修，让您享受到家一般的舒适与便利。'
  }
  return descriptionMap[type] || '暂无描述'
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  
  return `${year}-${month}-${day}`
}

// 计算入住天数
const calculateDays = (checkInDate, checkOutDate) => {
  if (!checkInDate || !checkOutDate) return 0
  
  const start = new Date(checkInDate)
  const end = new Date(checkOutDate)
  const diffTime = Math.abs(end - start)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  return diffDays
}

// 计算总价
const calculateTotalPrice = () => {
  if (!bookingForm.checkInDate || !bookingForm.checkOutDate || !selectedRoom.value.price) return 0
  
  const days = calculateDays(bookingForm.checkInDate, bookingForm.checkOutDate)
  return selectedRoom.value.price * days
}

// 搜索可用房间
const searchRooms = async () => {
  if (!filterForm.checkInDate || !filterForm.checkOutDate) {
    ElMessage.warning('请选择入住和退房日期')
    return
  }
  
  loading.value = true
  try {
    const params = {
      check_in_date: formatDate(filterForm.checkInDate),
      check_out_date: formatDate(filterForm.checkOutDate)
    }
    
    if (filterForm.roomType) {
      params.room_type = filterForm.roomType
    }
    
    const response = await axios.get('/api/booking/available-rooms/', { params })
    availableRooms.value = response.data.rooms || []
  } catch (error) {
    console.error('获取可用房间失败:', error)
    ElMessage.error('获取可用房间失败，请稍后重试')
    availableRooms.value = []
  } finally {
    loading.value = false
  }
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.checkInDate = null
  filterForm.checkOutDate = null
  filterForm.roomType = ''
  availableRooms.value = []
}

// 显示房间详情
const showRoomDetail = (room) => {
  selectedRoom.value = room
  detailDialogVisible.value = true
}

// 显示预订表单
const showBookingForm = (room) => {
  if (!filterForm.checkInDate || !filterForm.checkOutDate) {
    ElMessage.warning('请先选择入住和退房日期')
    return
  }
  
  selectedRoom.value = room
  bookingForm.roomId = room.id
  bookingForm.roomNumber = room.room_number
  bookingForm.roomType = room.room_type
  bookingForm.checkInDate = filterForm.checkInDate
  bookingForm.checkOutDate = filterForm.checkOutDate
  
  detailDialogVisible.value = false
  bookingDialogVisible.value = true
}

// 提交预订
const submitBooking = async () => {
  if (!bookingFormRef.value) return
  
  await bookingFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const bookingData = {
          room_id: bookingForm.roomId,
          check_in_date: formatDate(bookingForm.checkInDate),
          check_out_date: formatDate(bookingForm.checkOutDate),
          guest_name: bookingForm.guestName,
          guest_phone: bookingForm.guestPhone,
          guest_id_card: bookingForm.guestIdCard,
          guest_count: bookingForm.guestCount
        }
        
        const response = await axios.post('/api/booking/create/', bookingData)
        
        if (response.data && response.data.success) {
          bookingResult.value = response.data
          bookingDialogVisible.value = false
          codeDialogVisible.value = true
          
          // 重新搜索可用房间
          searchRooms()
        } else {
          ElMessage.error(response.data.error || '预订失败，请稍后重试')
        }
      } catch (error) {
        console.error('提交预订失败:', error)
        ElMessage.error(error.response?.data?.error || '提交预订失败，请稍后重试')
      }
    } else {
      return false
    }
  })
}

// 完成预订流程
const finishBooking = () => {
  codeDialogVisible.value = false
  resetBookingForm()
}

// 重置预订表单
const resetBookingForm = () => {
  bookingForm.roomId = ''
  bookingForm.roomNumber = ''
  bookingForm.roomType = ''
  bookingForm.checkInDate = null
  bookingForm.checkOutDate = null
  bookingForm.guestName = ''
  bookingForm.guestPhone = ''
  bookingForm.guestIdCard = ''
  bookingForm.guestCount = 1
  
  if (bookingFormRef.value) {
    bookingFormRef.value.resetFields()
  }
}

// 页面加载时设置默认日期
onMounted(() => {
  // 设置默认入住日期为今天
  const today = new Date()
  filterForm.checkInDate = today
  
  // 设置默认退房日期为明天
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  filterForm.checkOutDate = tomorrow
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

.room-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.room-card {
  transition: all 0.3s;
}

.room-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.room-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.room-header h3 {
  margin: 0;
  font-size: 18px;
}

.room-price {
  color: #f56c6c;
  font-weight: bold;
  font-size: 18px;
}

.room-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 10px;
}

.room-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.room-detail {
  padding: 10px;
}

.facility-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.facility-tag {
  margin-right: 0;
}

.total-price {
  color: #f56c6c;
  font-weight: bold;
  font-size: 18px;
}

.code-info {
  text-align: center;
  padding: 20px 0;
}

.highlight {
  color: #409eff;
  font-weight: bold;
  font-size: 18px;
}

.code-tip {
  margin-top: 20px;
  color: #e6a23c;
  font-size: 14px;
}
</style>