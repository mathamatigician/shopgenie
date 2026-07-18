<template>
  <div class="payments-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Payments & Receipts</h1>
        <p class="page-subtitle">View past transaction receipts and pay active orders</p>
      </div>
      <router-link to="/chat" class="btn btn-accent">
        <i class="fa-solid fa-microphone"></i>
        <span>Pay via Voice/AI Chat</span>
      </router-link>
    </div>

    <!-- Active Pending Payments Banner -->
    <div v-if="pendingOrders.length > 0" class="pending-alert glass-panel">
      <div class="alert-info">
        <i class="fa-solid fa-circle-exclamation alert-icon"></i>
        <div>
          <h4>You have {{ pendingOrders.length }} order(s) awaiting payment</h4>
          <p>Order #{{ pendingOrders[0].id }} for {{ pendingOrders[0].product }} (₹{{ pendingOrders[0].amount }})</p>
        </div>
      </div>
      <button @click="payOrder(pendingOrders[0].id)" class="btn btn-primary">
        Pay ₹{{ pendingOrders[0].amount }} Now
      </button>
    </div>

    <!-- Payments List Panel -->
    <div class="glass-panel main-panel">
      <h3 class="panel-title"><i class="fa-solid fa-receipt"></i> Transaction History</h3>

      <div v-if="loading" class="state-container">
        <i class="fa-solid fa-spinner fa-spin icon-spin"></i>
        <p>Fetching transaction records...</p>
      </div>

      <div v-else-if="payments.length === 0" class="state-container">
        <i class="fa-solid fa-credit-card empty-icon"></i>
        <h3>No Transaction History Yet</h3>
        <p>Transactions will appear here automatically when you complete payments.</p>
      </div>

      <div v-else class="table-responsive">
        <table class="payments-table">
          <thead>
            <tr>
              <th>Payment ID</th>
              <th>Order ID</th>
              <th>Method</th>
              <th>Status</th>
              <th>Amount</th>
              <th>Date & Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pay in payments" :key="pay.id">
              <td class="id-cell">{{ pay.id }}</td>
              <td class="order-cell">#{{ pay.order_id }}</td>
              <td class="method-cell">
                <i :class="getMethodIcon(pay.method)"></i>
                <span>{{ pay.method }}</span>
              </td>
              <td>
                <span :class="getStatusBadgeClass(pay.status)" class="badge">
                  {{ pay.status }}
                </span>
              </td>
              <td class="amount-cell">₹{{ pay.amount.toLocaleString() }}</td>
              <td class="date-cell">{{ formatDate(pay.date) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { paymentService, orderService } from '../services/api';

const payments = ref([]);
const pendingOrders = ref([]);
const loading = ref(true);

const loadData = async () => {
  loading.value = true;
  try {
    const [pData, oData] = await Promise.all([
      paymentService.getPayments(),
      orderService.getOrders()
    ]);
    payments.value = pData;
    pendingOrders.value = oData.filter(o => o.status === 'Pending');
  } catch (err) {
    console.error("Failed to load payment data", err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadData();
});

const getStatusBadgeClass = (status) => {
  if (status === 'Paid') return 'badge-paid';
  if (status === 'Refunded') return 'badge-negative';
  return 'badge-pending';
};

const getMethodIcon = (method) => {
  const m = method.toLowerCase();
  if (m.includes('visa')) return 'fa-brands fa-cc-visa text-blue';
  if (m.includes('mastercard')) return 'fa-brands fa-cc-mastercard text-red';
  if (m.includes('upi')) return 'fa-solid fa-mobile-screen-button text-green';
  return 'fa-solid fa-credit-card';
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleString([], { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
};

const payOrder = async (orderId) => {
  try {
    await paymentService.payOrder(orderId);
    await loadData();
  } catch (err) {
    alert("Payment error: " + (err.response?.data?.detail || err.message));
  }
};
</script>

<style scoped>
.payments-page {
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

.pending-alert {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  margin-bottom: 20px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.alert-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.alert-icon {
  font-size: 1.8rem;
  color: var(--accent-amber);
}

.alert-info h4 {
  font-weight: 700;
  font-size: 1rem;
}

.alert-info p {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.main-panel {
  padding: 24px;
}

.panel-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
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

.table-responsive {
  overflow-x: auto;
}

.payments-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.payments-table th {
  padding: 12px 16px;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
  border-bottom: 1px solid var(--border-color);
}

.payments-table td {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  font-size: 0.9rem;
}

.id-cell {
  font-family: monospace;
  font-weight: 700;
  color: var(--secondary);
}

.order-cell {
  font-family: monospace;
  font-weight: 700;
  color: var(--accent-cyan);
}

.method-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-blue { color: #60a5fa; }
.text-red { color: #f87171; }
.text-green { color: #34d399; }

.amount-cell {
  font-weight: 700;
  color: var(--accent-emerald);
}

.date-cell {
  font-size: 0.8rem;
  color: var(--text-muted);
}
</style>
