<template>
  <div class="dashboard-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Welcome back, {{ userName }} 👋</h1>
        <p class="page-subtitle">Here is your AI-powered shopping overview and order status</p>
      </div>
      <router-link to="/chat" class="btn btn-primary">
        <i class="fa-solid fa-comments"></i>
        <span>Open AI Chat Assistant</span>
      </router-link>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card glass-panel">
        <div class="stat-icon icon-indigo">
          <i class="fa-solid fa-box"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Total Orders</span>
          <span class="stat-value">{{ orders.length }}</span>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon icon-emerald">
          <i class="fa-solid fa-circle-check"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Paid & Completed</span>
          <span class="stat-value">{{ paidOrdersCount }}</span>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon icon-amber">
          <i class="fa-solid fa-clock"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Pending Payment</span>
          <span class="stat-value">{{ pendingOrdersCount }}</span>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon icon-cyan">
          <i class="fa-solid fa-indian-rupee-sign"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Total Spent</span>
          <span class="stat-value">₹{{ totalSpent.toLocaleString() }}</span>
        </div>
      </div>
    </div>

    <!-- Main Section: Recent Orders & Quick Chat Banner -->
    <div class="dashboard-main-grid">
      <!-- Recent Orders List -->
      <div class="orders-section glass-panel">
        <div class="section-header">
          <h3><i class="fa-solid fa-list-check"></i> Recent Orders</h3>
          <router-link to="/orders" class="view-all-link">View All</router-link>
        </div>

        <div v-if="loading" class="loading-state">
          <i class="fa-solid fa-spinner fa-spin"></i> Loading orders...
        </div>

        <div v-else-if="orders.length === 0" class="empty-state">
          <p>No orders yet! Click the button below to order using AI conversation.</p>
        </div>

        <div v-else class="orders-list">
          <div v-for="order in orders.slice(0, 4)" :key="order.id" class="order-item">
            <div class="order-info">
              <span class="order-id">#{{ order.id }}</span>
              <span class="order-prod">{{ order.product }} (x{{ order.quantity }})</span>
            </div>
            <div class="order-meta">
              <span class="order-amount">₹{{ order.amount }}</span>
              <span :class="getStatusBadgeClass(order.status)" class="badge">
                {{ order.status }}
              </span>
              <button 
                v-if="order.status === 'Pending'" 
                @click="payNow(order.id)" 
                class="btn btn-primary btn-xs"
              >
                Pay Now
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Banner & Quick Commands -->
      <div class="ai-banner glass-panel">
        <div class="banner-badge">🧞‍♂️ ShopGenie AI</div>
        <h2>Shopping Made Zero-Friction</h2>
        <p>No browsing 10 pages. Just tell ShopGenie what you need or ask to pay your bill!</p>

        <div class="quick-command-box">
          <span class="box-title">Popular Voice & Text Commands:</span>
          <router-link to="/chat" class="cmd-chip">
            <i class="fa-solid fa-keyboard"></i> "Order another keyboard"
          </router-link>
          <router-link to="/chat" class="cmd-chip">
            <i class="fa-solid fa-credit-card"></i> "Pay for my latest order"
          </router-link>
          <router-link to="/chat" class="cmd-chip">
            <i class="fa-solid fa-comment-dots"></i> "Packaging was poor for order 101"
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { orderService, paymentService } from '../services/api';
import { useAuthStore } from '../store/auth';

const router = useRouter();
const { state: authState } = useAuthStore();
const orders = ref([]);
const loading = ref(true);

const userName = computed(() => authState.user?.name || 'User');

const fetchOrders = async () => {
  loading.value = true;
  try {
    orders.value = await orderService.getOrders();
  } catch (err) {
    console.error("Failed to load orders", err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchOrders();
});

const paidOrdersCount = computed(() => orders.value.filter(o => o.status === 'Paid' || o.status === 'Delivered').length);
const pendingOrdersCount = computed(() => orders.value.filter(o => o.status === 'Pending').length);
const totalSpent = computed(() => orders.value.reduce((acc, o) => acc + (o.status !== 'Cancelled' ? o.amount : 0), 0));

const getStatusBadgeClass = (status) => {
  if (status === 'Paid') return 'badge-paid';
  if (status === 'Delivered') return 'badge-delivered';
  return 'badge-pending';
};

const payNow = async (orderId) => {
  try {
    await paymentService.payOrder(orderId);
    await fetchOrders();
  } catch (err) {
    alert("Payment error: " + (err.response?.data?.detail || err.message));
  }
};
</script>

<style scoped>
.dashboard-page {
  max-width: 1100px;
  margin: 24px auto;
  padding: 0 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.icon-indigo { background: rgba(99, 102, 241, 0.15); color: var(--primary); }
.icon-emerald { background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); }
.icon-amber { background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); }
.icon-cyan { background: rgba(6, 182, 212, 0.15); color: var(--accent-cyan); }

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 600;
}

.stat-value {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-main);
}

.dashboard-main-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 20px;
}

@media (max-width: 900px) {
  .dashboard-main-grid {
    grid-template-columns: 1fr;
  }
}

.orders-section {
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 1.1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-all-link {
  font-size: 0.8rem;
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
}

.loading-state, .empty-state {
  padding: 30px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.order-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.order-id {
  font-family: monospace;
  font-weight: 700;
  color: var(--accent-cyan);
}

.order-prod {
  font-weight: 600;
  font-size: 0.9rem;
}

.order-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.order-amount {
  font-weight: 700;
  font-size: 0.95rem;
}

.btn-xs {
  padding: 4px 10px;
  font-size: 0.75rem;
}

.ai-banner {
  padding: 28px 24px;
  background: linear-gradient(135deg, rgba(30, 41, 67, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.banner-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--accent-cyan);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}

.ai-banner h2 {
  font-size: 1.35rem;
  font-weight: 800;
  margin-bottom: 8px;
}

.ai-banner p {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 20px;
}

.quick-command-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.box-title {
  font-size: 0.75rem;
  color: var(--text-subtle);
  font-weight: 700;
  text-transform: uppercase;
}

.cmd-chip {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  color: var(--text-main);
  font-size: 0.82rem;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.cmd-chip:hover {
  background: var(--primary-light);
  border-color: var(--border-glow);
  transform: translateX(4px);
}
</style>
