<template>
 <div class="ask-container">
    <h2 class="page-title">服务请求</h2>
    
    <el-tabs v-model="activeTab" class="service-tabs">
      <!-- 餐饮服务标签页 -->
      <el-tab-pane label="餐饮服务" name="food">
        <el-card class="menu-card">
          <template #header>
            <div class="card-header">
              <span>菜单</span>
              <el-button type="primary" size="small" @click="showCart" :disabled="cartItems.length === 0">
                购物车 ({{ cartItems.length }})
              </el-button>
            </div>
          </template>
          
          <!-- 菜品分类 -->
          <el-tabs v-model="foodCategory">
            <el-tab-pane v-for="category in foodCategories" :key="category.value" :label="category.label" :name="category.value">
              <div class="food-list">
                <el-card v-for="food in getFoodsByCategory(category.value)" :key="food.id" class="food-item">
                  <div class="food-content">
                    <div class="food-info">
                      <h3>{{ food.name }}</h3>
                      <p class="food-desc">{{ food.description }}</p>
                      <div class="food-price">¥{{ food.price }}</div>
                    </div>
                    <div class="food-action">
                      <el-button type="primary" size="small" @click="addToCart(food)">添加</el-button>
                    </div>
                  </div>
                </el-card>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-tab-pane>
      
      <!-- 卫生服务标签页 -->
      <el-tab-pane label="卫生服务" name="cleaning">
        <el-card class="cleaning-card">
          <el-form :model="cleaningForm" label-width="100px" :rules="cleaningRules" ref="cleaningFormRef">
            <el-form-item label="服务类型" prop="serviceType">
              <el-radio-group v-model="cleaningForm.serviceType">
                <el-radio label="cleaning">房间清洁</el-radio>
                <el-radio label="repair">设施维修</el-radio>
              </el-radio-group>
            </el-form-item>
            
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
                placeholder="请详细描述您的需求或需要维修的设施"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitCleaningRequest">提交请求</el-button>
              <el-button @click="resetCleaningForm">重置</el-button>
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
                <p v-if="record.type === 'food'">订单内容: {{ record.items.map(item => `${item.name} x${item.quantity}`).join(', ') }}</p>
                <p v-else>详细说明: {{ record.description }}</p>
                <p v-if="record.expectedTime">期望时间: {{ record.expectedTime }}</p>
                <p v-if="record.completedTime">完成时间: {{ record.completedTime }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 购物车对话框 -->
    <el-dialog v-model="cartDialogVisible" title="购物车" width="50%">
      <el-table :data="cartItems" style="width: 100%">
        <el-table-column prop="name" label="菜品名称" />
        <el-table-column label="数量" width="150">
          <template #default="scope">
            <el-input-number v-model="scope.row.quantity" :min="1" :max="10" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="单价" width="100">
          <template #default="scope">
            <span>¥{{ scope.row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column label="小计" width="100">
          <template #default="scope">
            <span class="subtotal">¥{{ (scope.row.price * scope.row.quantity).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="danger" size="small" @click="removeFromCart(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="cart-footer">
        <div class="cart-total">
          总计: <span class="total-price">¥{{ calculateTotal() }}</span>
        </div>
        <div class="cart-actions">
          <el-button @click="cartDialogVisible = false">继续点餐</el-button>
          <el-button type="primary" @click="submitFoodOrder">提交订单</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 当前激活的标签页
const activeTab = ref('food')

// 餐饮服务相关
const foodCategory = ref('main')
const foodCategories = [
  { label: '主食', value: 'main' },
  { label: '小吃', value: 'snack' },
  { label: '饮料', value: 'drink' },
  { label: '甜点', value: 'dessert' }
]

// 模拟菜品数据
const foodList = [
  { id: 1, name: '牛肉面', category: 'main', price: 38, description: '精选牛肉，配以手工面条，汤底浓郁' },
  { id: 2, name: '宫保鸡丁', category: 'main', price: 42, description: '鸡肉鲜嫩，配以花生和干辣椒，口感丰富' },
  { id: 3, name: '水煮鱼', category: 'main', price: 58, description: '新鲜鱼肉，麻辣鲜香，配以豆芽和青菜' },
  { id: 4, name: '炒饭', category: 'main', price: 28, description: '蛋香浓郁，配以各种蔬菜和肉类' },
  { id: 5, name: '薯条', category: 'snack', price: 18, description: '外酥里嫩，配以番茄酱' },
  { id: 6, name: '鸡翅', category: 'snack', price: 26, description: '外脆里嫩，香辣可口' },
  { id: 7, name: '可乐', category: 'drink', price: 8, description: '冰镇可口可乐，提神解渴' },
  { id: 8, name: '果汁', category: 'drink', price: 12, description: '新鲜水果制作，营养健康' },
  { id: 9, name: '提拉米苏', category: 'dessert', price: 22, description: '经典意式甜点，口感细腻' },
  { id: 10, name: '芝士蛋糕', category: 'dessert', price: 24, description: '浓郁芝士风味，甜而不腻' }
]

// 根据分类获取菜品
const getFoodsByCategory = (category) => {
  return foodList.filter(food => food.category === category)
}

// 购物车相关
const cartItems = ref([])
const cartDialogVisible = ref(false)

// 添加到购物车
const addToCart = (food) => {
  const existingItem = cartItems.value.find(item => item.id === food.id)
  if (existingItem) {
    existingItem.quantity++
  } else {
    cartItems.value.push({
      id: food.id,
      name: food.name,
      price: food.price,
      quantity: 1
    })
  }
  ElMessage.success(`已添加 ${food.name} 到购物车`)
}

// 从购物车移除
const removeFromCart = (item) => {
  const index = cartItems.value.findIndex(cartItem => cartItem.id === item.id)
  if (index !== -1) {
    cartItems.value.splice(index, 1)
  }
}

// 计算总价
const calculateTotal = () => {
  return cartItems.value.reduce((total, item) => total + item.price * item.quantity, 0).toFixed(2)
}

// 显示购物车
const showCart = () => {
  cartDialogVisible.value = true
}

// 提交餐饮订单
const submitFoodOrder = () => {
  if (cartItems.value.length === 0) {
    ElMessage.warning('购物车为空')
    return
  }
  
  // 这里应该调用API提交订单
  ElMessageBox.confirm(
    '确认提交订单吗？',
    '提交订单',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    // 添加到服务记录
    serviceHistory.value.unshift({
      type: 'food',
      status: 'processing',
      requestTime: new Date().toLocaleString(),
      items: JSON.parse(JSON.stringify(cartItems.value)),
      totalPrice: calculateTotal()
    })
    
    ElMessage.success('订单已提交')
    cartItems.value = []
    cartDialogVisible.value = false
  }).catch(() => {
    // 用户取消操作
  })
}

// 卫生服务相关
const cleaningFormRef = ref(null)
const cleaningForm = reactive({
  serviceType: 'cleaning',
  expectedTime: null,
  description: ''
})

// 表单验证规则
const cleaningRules = {
  serviceType: [
    { required: true, message: '请选择服务类型', trigger: 'change' }
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
        type: cleaningForm.serviceType,
        status: 'pending',
        requestTime: new Date().toLocaleString(),
        expectedTime: cleaningForm.expectedTime ? cleaningForm.expectedTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : null,
        description: cleaningForm.description
      })
      
      ElMessage.success('服务请求已提交')
      resetCleaningForm()
    } else {
      ElMessage.error('请正确填写表单')
    }
  })
}

// 重置卫生服务表单
const resetCleaningForm = () => {
  cleaningFormRef.value.resetFields()
}

// 服务记录相关
const serviceHistory = ref([
  {
    type: 'food',
    status: 'completed',
    requestTime: '2023-06-01 18:30:00',
    completedTime: '2023-06-01 19:15:00',
    items: [
      { name: '牛肉面', quantity: 1, price: 38 },
      { name: '可乐', quantity: 2, price: 8 }
    ],
    totalPrice: '54.00'
  },
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
    status: 'processing',
    requestTime: '2023-06-02 09:15:00',
    expectedTime: '11:00',
    description: '浴室水龙头漏水，需要维修'
  }
])

// 获取服务类型名称
const getServiceTypeName = (type) => {
  const typeMap = {
    'food': '餐饮服务',
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

.menu-card, .cleaning-card, .history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.food-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.food-item {
  height: 100%;
}

.food-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.food-info {
  flex-grow: 1;
}

.food-desc {
  color: #606266;
  font-size: 14px;
  margin: 8px 0;
}

.food-price {
  color: #f56c6c;
  font-weight: bold;
  margin-bottom: 10px;
}

.food-action {
  margin-top: auto;
}

.cart-footer {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-price, .subtotal {
  color: #f56c6c;
  font-weight: bold;
}

.history-item-card {
  margin-bottom: 10px;
}
</style>