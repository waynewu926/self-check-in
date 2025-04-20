<template>
  <div class="record-container">
    <h2 class="page-title">预订记录</h2>
    
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" :inline="true">
        <el-form-item label="预订时间">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="filterForm.status" placeholder="选择状态">
            <el-option label="全部" value="" />
            <el-option label="待入住" value="pending" />
            <el-option label="已入住" value="checked-in" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchRecords">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 预订记录列表 -->
    <el-card class="record-list-card">
      <template #header>
        <div class="card-header">
          <span>预订记录列表</span>
          <el-tag v-if="records.length > 0" type="info">共 {{ records.length }} 条记录</el-tag>
        </div>
      </template>
      
      <el-empty v-if="records.length === 0" description="暂无预订记录"></el-empty>
      
      <el-table v-else :data="records" style="width: 100%">
        <el-table-column prop="orderNumber" label="订单号" width="180" />
        <el-table-column prop="roomInfo" label="房间信息" width="150">
          <template #default="scope">
            {{ getRoomTypeName(scope.row.roomType) }} - {{ scope.row.roomNumber }}
          </template>
        </el-table-column>
        <el-table-column label="入住时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.checkInDate) }}
          </template>
        </el-table-column>
        <el-table-column label="退房时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.checkOutDate) }}
          </template>
        </el-table-column>
        <el-table-column prop="price" label="总价" width="120">
          <template #default="scope">
            <span class="price">¥{{ scope.row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusTag(scope.row.status)">
              {{ getStatusName(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="showOrderDetail(scope.row)">详情</el-button>
            <el-button 
              v-if="scope.row.status === 'pending'" 
              type="danger" 
              size="small" 
              @click="cancelOrder(scope.row)">取消预订</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalRecords"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 订单详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="订单详情" width="60%">
      <div v-if="selectedOrder.orderNumber" class="order-detail">
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="订单号">{{ selectedOrder.orderNumber }}</el-descriptions-item>
          <el-descriptions-item label="预订时间">{{ formatDate(selectedOrder.orderTime) }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getStatusTag(selectedOrder.status)">
              {{ getStatusName(selectedOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="支付方式">{{ selectedOrder.paymentMethod }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="center">房间信息</el-divider>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="房间类型">{{ getRoomTypeName(selectedOrder.roomType) }}</el-descriptions-item>
          <el-descriptions-item label="房间号">{{ selectedOrder.roomNumber }}</el-descriptions-item>
          <el-descriptions-item label="入住日期">{{ formatDate(selectedOrder.checkInDate) }}</el-descriptions-item>
          <el-descriptions-item label="退房日期">{{ formatDate(selectedOrder.checkOutDate) }}</el-descriptions-item>
          <el-descriptions-item label="入住天数">{{ selectedOrder.days }}晚</el-descriptions-item>
          <el-descriptions-item label="房间单价">¥{{ selectedOrder.roomPrice }}/晚</el-descriptions-item>
          <el-descriptions-item label="总价">
            <span class="price">¥{{ selectedOrder.price }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="房间设施" :span="2">
            <el-tag v-for="facility in selectedOrder.facilities" :key="facility" size="small" class="facility-tag">
              {{ facility }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="center">入住人信息</el-divider>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ selectedOrder.guestName }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">{{ maskIdCard(selectedOrder.idCard) }}</el-descriptions-item>
          <el-descriptions-item label="手机号码">{{ maskPhone(selectedOrder.phone) }}</el-descriptions-item>
          <el-descriptions-item label="入住人数">{{ selectedOrder.guestCount }}人</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ selectedOrder.remarks || '无' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button 
            v-if="selectedOrder.status === 'pending'" 
            type="danger" 
            @click="cancelOrder(selectedOrder)">取消预订</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 筛选表单
const filterForm = reactive({
  dateRange: [],
  status: ''
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const totalRecords = ref(100) // 模拟总记录数

// 详情对话框
const detailDialogVisible = ref(false)
const selectedOrder = ref({})

// 获取房间类型名称
const getRoomTypeName = (type) => {
  const typeMap = {
    '0': '标准间',
    '1': '豪华间',
    '2': '套房'
  }
  return typeMap[type] || type
}

// 获取状态名称
const getStatusName = (status) => {
  const statusMap = {
    'pending': '待入住',
    'checked-in': '已入住',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

// 获取状态标签样式
const getStatusTag = (status) => {
  const tagMap = {
    'pending': 'warning',
    'checked-in': 'success',
    'completed': 'info',
    'cancelled': 'danger'
  }
  return tagMap[status] || ''
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

// 身份证号脱敏
const maskIdCard = (idCard) => {
  if (!idCard || idCard.length < 15) return idCard
  return idCard.replace(/^(.{6})(?:\d+)(.{4})$/, '$1********$2')
}

// 模拟预订记录数据
const records = ref([
  {
    orderNumber: 'R202305150001',
    roomType: '0', // 标准间
    roomNumber: '201',
    checkInDate: new Date('2023-05-20'),
    checkOutDate: new Date('2023-05-22'),
    days: 2,
    roomPrice: 399,
    price: 798,
    status: 'completed',
    orderTime: new Date('2023-05-15 14:30:00'),
    paymentMethod: '微信支付',
    guestName: '张三',
    idCard: '110101199001011234',
    phone: '13800138000',
    guestCount: 2,
    remarks: '',
    facilities: ['免费WiFi', '空调', '冰箱', '电视']
  },
  {
    orderNumber: 'R202305200002',
    roomType: '1', // 豪华间
    roomNumber: '301',
    checkInDate: new Date('2023-05-25'),
    checkOutDate: new Date('2023-05-27'),
    days: 2,
    roomPrice: 599,
    price: 1198,
    status: 'pending',
    orderTime: new Date('2023-05-20 10:15:00'),
    paymentMethod: '支付宝',
    guestName: '李四',
    idCard: '310101199202022345',
    phone: '13900139000',
    guestCount: 2,
    remarks: '希望安排高层房间',
    facilities: ['免费WiFi', '空调', '冰箱', '电视', '洗衣机', '烘干机']
  },
  {
    orderNumber: 'R202305250003',
    roomType: '2', // 套房
    roomNumber: '501',
    checkInDate: new Date('2023-06-01'),
    checkOutDate: new Date('2023-06-03'),
    days: 2,
    roomPrice: 899,
    price: 1798,
    status: 'checked-in',
    orderTime: new Date('2023-05-25 16:45:00'),
    paymentMethod: '银行卡',
    guestName: '王五',
    idCard: '440101199303033456',
    phone: '13700137000',
    guestCount: 3,
    remarks: '需要加床',
    facilities: ['免费WiFi', '空调', '冰箱', '电视', '洗衣机', '烘干机', '客厅', '投影仪']
  },
  {
    orderNumber: 'R202306010004',
    roomType: '0', // 标准间
    roomNumber: '202',
    checkInDate: new Date('2023-06-10'),
    checkOutDate: new Date('2023-06-12'),
    days: 2,
    roomPrice: 399,
    price: 798,
    status: 'cancelled',
    orderTime: new Date('2023-06-01 09:20:00'),
    paymentMethod: '微信支付',
    guestName: '赵六',
    idCard: '510101199404044567',
    phone: '13600136000',
    guestCount: 1,
    remarks: '',
    facilities: ['免费WiFi', '空调', '冰箱', '电视']
  }
])

// 搜索记录
const searchRecords = () => {
  // 这里应该调用API获取符合条件的预订记录
  // 模拟API调用
  ElMessage.success('搜索成功')
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.dateRange = []
  filterForm.status = ''
}

// 显示订单详情
const showOrderDetail = (order) => {
  selectedOrder.value = order
  detailDialogVisible.value = true
}

// 取消预订
const cancelOrder = (order) => {
  ElMessageBox.confirm(
    `确定要取消订单 ${order.orderNumber} 吗？`,
    '取消预订',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 这里应该调用API取消预订
    // 模拟API调用
    order.status = 'cancelled'
    ElMessage.success('预订已取消')
    detailDialogVisible.value = false
  }).catch(() => {
    // 用户取消操作
  })
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  // 重新加载数据
  searchRecords()
}

// 处理页码变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  // 重新加载数据
  searchRecords()
}
</script>

<style scoped>
.record-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
}

.record-list-card {
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.order-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.facility-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}
</style>