<template>
  <div class="orders-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">My Orders</h1>
        <p class="page-subtitle">Track your orders, view statuses, and make instant payments</p>
      </div>
      <router-link to="/chat" class="btn btn-primary">
        <i class="fa-solid fa-plus"></i>
        <span>Create New Order via AI</span>
      </router-link>
    </div>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab" 
        @click="activeTab = tab" 
        class="tab-btn" 
        :class="{ active: activeTab === tab }"
      >
        {{ tab }}
        <span class="tab-count">{{ getTabCount(tab) }}</span>
      </button>
    </div>

    <!-- Orders Table / List Card -->
    <div class="glass-panel main-panel">
      <div v-if="loading" class="state-container">
        <i class="fa-solid fa-spinner fa-spin icon-spin"></i>
        <p>Loading your orders...</p>
      </div>

      <div v-else-if="filteredOrders.length === 0" class="state-container">
        <i class="fa-solid fa-box-open empty-icon"></i>
        <h3>No {{ activeTab !== 'All' ? activeTab : '' }} Orders Found</h3>
        <p>Start a conversation with ShopGenie to order products instantly!</p>
        <router-link to="/chat" class="btn btn-secondary mt-12">
          Talk to ShopGenie
        </router-link>
      </div>

      <div v-else class="table-responsive">
        <table class="orders-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Items & Product</th>
              <th>Quantity</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Date</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in filteredOrders" :key="order.id">
              <td class="id-cell">#{{ order.id }}</td>
              <td class="prod-cell">
                <span class="prod-icon">{{ getProductEmoji(order.product) }}</span>
                <span class="prod-name">{{ order.product }}</span>
              </td>
              <td>{{ order.quantity }}</td>
              <td class="amount-cell">₹{{ order.amount.toLocaleString() }}</td>
              <td>
                <span :class="getStatusBadgeClass(order.status)" class="badge">
                  {{ order.status }}
                </span>
              </td>
              <td class="date-cell">{{ formatDate(order.date) }}</td>
              <td class="text-right actions-cell">
                <button 
                  v-if="order.status === 'Pending'" 
                  @click="handlePay(order.id)" 
                  class="btn btn-primary btn-xs"
                >
                  <i class="fa-solid fa-credit-card"></i> Pay Now
                </button>
                <router-link 
                  to="/chat" 
                  class="btn btn-secondary btn-xs"
                  title="Give feedback or request support"
                >
                  <i class="fa-solid fa-comment"></i> Feedback
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { orderService, paymentService } from '../services/api';

const orders = ref([]);
const loading = ref(true);
const activeTab = ref('All');
const tabs = ['All', 'Pending', 'Paid', 'Delivered'];

const fetchOrders = async () => {
  loading.value = true;
  try {
    orders.value = await orderService.getOrders();
  } catch (err) {
    console.error("Error fetching orders", err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchOrders();
});

const filteredOrders = computed(() => {
  if (activeTab.value === 'All') return orders.value;
  return orders.value.filter(o => o.status === activeTab.value);
});

const getTabCount = (tab) => {
  if (tab === 'All') return orders.value.length;
  return orders.value.filter(o => o.status === tab).length;
};

const getStatusBadgeClass = (status) => {
  if (status === 'Paid') return 'badge-paid';
  if (status === 'Delivered') return 'badge-delivered';
  return 'badge-pending';
};

const getProductEmoji = (productName) => {
  const name = productName.toLowerCase();
  if (name.includes('keyboard')) return '⌨️';
  if (name.includes('mouse')) return '🖱️';
  if (name.includes('stand')) return '💻';
  if (name.includes('bag')) return '🎒';
  if (name.includes('headphone')) return '🎧';
  if (name.includes('hub')) return '🔌';
  return '📦';
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
};

const handlePay = async (orderId) => {
  try {
    await paymentService.payOrder(orderId);
    await fetchOrders();
  } catch (err) {
    alert("Payment error: " + (err.response?.data?.detail || err.message));
  }
};
</script>

<style scoped>
.orders-page {
  max-width: 1100px;
  margin: 24px auto;
  padding: 0 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--text-main);
}

.page-subtitle {
  font-size: 0.88rem;
  color: var(--text-muted);
}

.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tab-btn {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.tab-btn:hover, .tab-btn.active {
  background: var(--primary-light);
  color: var(--text-main);
  border-color: var(--primary);
}

.tab-count {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 7px;
  border-radius: 9999px;
  font-size: 0.72rem;
}

.main-panel {
  padding: 20px;
}

.state-container {
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 12px;
  color: var(--text-subtle);
}

.icon-spin {
  font-size: 2rem;
  color: var(--primary);
  margin-bottom: 12px;
}

.mt-12 {
  margin-top: 12px;
}

.table-responsive {
  overflow-x: auto;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.orders-table th {
  padding: 12px 16px;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
  border-bottom: 1px solid var(--border-color);
}

.orders-table td {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  font-size: 0.9rem;
}

.id-cell {
  font-family: monospace;
  font-weight: 700;
  color: var(--accent-cyan);
}

.prod-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.prod-icon {
  font-size: 1.2rem;
}

.amount-cell {
  font-weight: 700;
  color: var(--text-main);
}

.date-cell {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.text-right {
  text-align: right;
}

.actions-cell {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-xs {
  padding: 5px 10px;
  font-size: 0.75rem;
}
</style>
