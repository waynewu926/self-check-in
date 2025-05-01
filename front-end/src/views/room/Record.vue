<template>
  <div class="record-container">
    <h2 class="page-title">预订记录</h2>
    
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" :inline="true">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="filterForm.status" placeholder="选择订单状态">
            <el-option label="全部" value="" />
            <el-option label="待入住" value="1" />
            <el-option label="已入住" value="2" />
            <el-option label="已完成" value="3" />
            <el-option label="已取消" value="0" />
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
        </div>
      </template>
      
      <el-empty v-if="bookings.length === 0" description="暂无预订记录"></el-empty>
      
      <el-table v-else :data="bookings" style="width: 100%" v-loading="loading">
        <el-table-column prop="booking_number" label="订单号" width="120" />
        <el-table-column label="房间信息" width="150">
          <template #default="scope">
            {{ scope.row.room_type_name }} - {{ scope.row.room_number }}
          </template>
        </el-table-column>
        <el-table-column prop="check_in_date" label="入住日期" width="120" />
        <el-table-column prop="check_out_date" label="退房日期" width="120" />
        <el-table-column label="入住天数" width="100">
          <template #default="scope">
            {{ calculateDays(scope.row.check_in_date, scope.row.check_out_date) }}天
          </template>
        </el-table-column>
        <el-table-column label="总价" width="120">
          <template #default="scope">
            <span class="price">¥{{ scope.row.total_price }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusTag(scope.row.booking_status)">
              {{ scope.row.booking_status_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="showOrderDetail(scope.row)">详情</el-button>
            <el-button 
              v-if="scope.row.booking_status === '1' || scope.row.booking_status === 1" 
              type="danger" 
              size="small" 
              @click="cancelOrder(scope.row)"
            >
              取消
            </el-button>
            <el-button 
              v-if="scope.row.booking_status === '3' || scope.row.booking_status === 3" 
              type="primary" 
              size="small" 
              @click="showCommentDialog(scope.row)"
              :disabled="!!scope.row.comment"
            >
              {{ scope.row.comment ? '已评价' : '评价' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[5, 10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalRecords"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 订单详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="订单详情" width="60%">
      <div v-if="selectedOrder.id" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ selectedOrder.booking_number }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTag(selectedOrder.booking_status)">
              {{ selectedOrder.booking_status_name }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="房间信息">
            {{ selectedOrder.room_type_name }} - {{ selectedOrder.room_number }}
          </el-descriptions-item>
          <el-descriptions-item label="价格">¥{{ selectedOrder.total_price }}</el-descriptions-item>
          <el-descriptions-item label="入住日期">{{ selectedOrder.check_in_date }}</el-descriptions-item>
          <el-descriptions-item label="退房日期">{{ selectedOrder.check_out_date }}</el-descriptions-item>
          <el-descriptions-item label="入住天数">
            {{ calculateDays(selectedOrder.check_in_date, selectedOrder.check_out_date) }}天
          </el-descriptions-item>
          <el-descriptions-item label="入住人数">{{ selectedOrder.guest_count }}人</el-descriptions-item>
          <el-descriptions-item label="入住人">{{ selectedOrder.guest_name }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ maskPhone(selectedOrder.guest_phone) }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">{{ maskIdCard(selectedOrder.guest_id_card) }}</el-descriptions-item>
          <el-descriptions-item label="验证码" v-if="selectedOrder.code">{{ selectedOrder.code }}</el-descriptions-item>
          <el-descriptions-item label="评价" :span="2" v-if="selectedOrder.comment">
            {{ selectedOrder.comment }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button 
            v-if="selectedOrder.booking_status === '1' || selectedOrder.booking_status === 1" 
            type="danger" 
            @click="cancelOrder(selectedOrder)"
          >
            取消预订
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 评价对话框 -->
    <el-dialog v-model="commentDialogVisible" title="评价住宿体验" width="50%">
      <el-form :model="commentForm" label-width="100px" ref="commentFormRef">
        <el-form-item label="总体评分">
          <el-rate v-model="commentForm.rating" :colors="colors" show-score />
        </el-form-item>
        <el-form-item label="评价内容">
          <el-input 
            v-model="commentForm.comment" 
            type="textarea" 
            :rows="4" 
            placeholder="请分享您的住宿体验..."
          />
        </el-form-item>
        <el-form-item label="环境评分">
          <el-rate v-model="commentForm.environmentRating" />
        </el-form-item>
        <el-form-item label="服务评分">
          <el-rate v-model="commentForm.serviceRating" />
        </el-form-item>
        <el-form-item label="设施评分">
          <el-rate v-model="commentForm.facilityRating" />
        </el-form-item>
        <el-form-item label="卫生评分">
          <el-rate v-model="commentForm.cleanlinessRating" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="commentDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitComment">提交评价</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 筛选表单
const filterForm = reactive({
  dateRange: [],
  status: ''
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const totalRecords = ref(0)
const loading = ref(false)

// 详情对话框
const detailDialogVisible = ref(false)
const selectedOrder = ref({})

// 预订记录数据
const bookings = ref([])

// 获取状态标签样式
const getStatusTag = (status) => {
  const tagMap = {
    '待入住': 'warning',
    '已入住': 'success',
    '已完成': 'info',
    '已取消': 'danger',
    '1': 'warning',
    '2': 'success',
    '3': 'info',
    '0': 'danger'
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

// 计算入住天数
const calculateDays = (checkInDate, checkOutDate) => {
  if (!checkInDate || !checkOutDate) return 0
  
  const start = new Date(checkInDate)
  const end = new Date(checkOutDate)
  const diffTime = Math.abs(end - start)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  return diffDays
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

// 获取预订记录数据
const fetchBookings = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.start_date = formatDate(filterForm.dateRange[0])
      params.end_date = formatDate(filterForm.dateRange[1])
    }
    
    if (filterForm.status) {
      params.status = filterForm.status
    }
    
    // 移除 withCredentials 配置，因为已在 main.js 中全局设置
    const response = await axios.get('/api/booking/list/', { params })
    
    // 处理响应数据
    if (response.data && response.data.bookings) {
      bookings.value = response.data.bookings.map(booking => {
        // 添加状态名称
        const statusMap = {
          '0': '已取消',
          '1': '待入住',
          '2': '已入住',
          '3': '已完成'
        }
        return {
          ...booking,
          booking_status_name: statusMap[booking.booking_status] || booking.booking_status,
          room_type_name: getRoomTypeName(booking.room_type)
        }
      })
      totalRecords.value = response.data.total || 0
    } else {
      bookings.value = []
      totalRecords.value = 0
    }
  } catch (error) {
    console.error('获取预订记录失败:', error)
    ElMessage.error('获取预订记录失败，请稍后重试')
    bookings.value = []
    totalRecords.value = 0
  } finally {
    loading.value = false
  }
}

// 获取房间类型名称
const getRoomTypeName = (type) => {
  const typeMap = {
    '1': '标准间',
    '2': '豪华间',
    '3': '套房'
  }
  return typeMap[type] || type
}

// 搜索记录
const searchRecords = () => {
  currentPage.value = 1
  fetchBookings()
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.dateRange = []
  filterForm.status = ''
  searchRecords()
}

// 显示订单详情
const showOrderDetail = (order) => {
  selectedOrder.value = order
  detailDialogVisible.value = true
}

// 取消预订
const cancelOrder = (order) => {
  ElMessageBox.confirm(
    `确定要取消订单 ${order.booking_number} 吗？`,
    '取消预订',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.post(`/api/booking/update-status/${order.id}/`, {
        status: 0  // 已取消
      })
      ElMessage.success('预订已取消')
      fetchBookings()
      detailDialogVisible.value = false
    } catch (error) {
      console.error('取消预订失败:', error)
      ElMessage.error(error.response?.data?.error || '取消预订失败，请稍后重试')
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  fetchBookings()
}

// 处理页码变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchBookings()
}

// 评价相关
const commentDialogVisible = ref(false)
const commentFormRef = ref(null)
const commentForm = reactive({
  rating: 5,
  comment: '',
  environmentRating: 5,
  serviceRating: 5,
  facilityRating: 5,
  cleanlinessRating: 5
})

// 评分颜色
const colors = ['#99A9BF', '#F7BA2A', '#FF9900']

// 显示评价对话框
const showCommentDialog = (order) => {
  selectedOrder.value = order
  // 重置评价表单
  commentForm.rating = 5
  commentForm.comment = ''
  commentForm.environmentRating = 5
  commentForm.serviceRating = 5
  commentForm.facilityRating = 5
  commentForm.cleanlinessRating = 5
  commentDialogVisible.value = true
}

// 提交评价
const submitComment = async () => {
  if (!commentForm.comment.trim()) {
    ElMessage.warning('请填写评价内容')
    return
  }
  
  try {
    // 计算平均评分
    const avgRating = (
      commentForm.rating + 
      commentForm.environmentRating + 
      commentForm.serviceRating + 
      commentForm.facilityRating + 
      commentForm.cleanlinessRating
    ) / 5
    
    // 构建评价内容
    const commentData = {
      comment: commentForm.comment,
      rating: avgRating.toFixed(1),
      details: {
        environment: commentForm.environmentRating,
        service: commentForm.serviceRating,
        facility: commentForm.facilityRating,
        cleanliness: commentForm.cleanlinessRating
      }
    }
    
    await axios.post(`/api/booking/add-comment/${selectedOrder.value.id}/`, commentData)
    
    ElMessage.success('评价提交成功')
    commentDialogVisible.value = false
    fetchBookings()
  } catch (error) {
    console.error('提交评价失败:', error)
    ElMessage.error(error.response?.data?.error || '提交评价失败，请稍后重试')
  }
}

// 页面加载时获取预订记录
onMounted(() => {
  fetchBookings()
})
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
  padding: 10px;
}
</style>