<template>
  <nav class="navbar glass-panel">
    <div class="nav-container">
      <!-- Brand Logo -->
      <router-link to="/" class="brand">
        <div class="brand-icon">🧞‍♂️</div>
        <div class="brand-text">
          <span class="brand-name">ShopGenie</span>
          <span class="brand-tag">AI Commerce</span>
        </div>
      </router-link>

      <!-- Navigation Links -->
      <div v-if="isAuthenticated" class="nav-links">
        <router-link to="/" class="nav-item" active-class="active">
          <i class="fa-solid fa-chart-pie"></i>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/orders" class="nav-item" active-class="active">
          <i class="fa-solid fa-box"></i>
          <span>Orders</span>
        </router-link>
        <router-link to="/payments" class="nav-item" active-class="active">
          <i class="fa-solid fa-credit-card"></i>
          <span>Payments</span>
        </router-link>
        <router-link to="/chat" class="nav-item nav-item-chat" active-class="active">
          <i class="fa-solid fa-robot"></i>
          <span>AI Assistant</span>
          <span class="pulse-dot"></span>
        </router-link>
      </div>

      <!-- User Menu -->
      <div v-if="isAuthenticated" class="user-menu">
        <div class="user-info">
          <div class="avatar">{{ userInitial }}</div>
          <div class="user-details">
            <span class="user-name">{{ user?.name || 'User' }}</span>
            <span class="user-email">{{ user?.email }}</span>
          </div>
        </div>
        <button @click="handleLogout" class="btn btn-secondary btn-sm" title="Log out">
          <i class="fa-solid fa-right-from-bracket"></i>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

const router = useRouter();
const { state, isAuthenticated, logout } = useAuthStore();

const user = computed(() => state.user);
const userInitial = computed(() => user.value?.name ? user.value.name.charAt(0).toUpperCase() : 'U');

const handleLogout = () => {
  logout();
  router.push('/login');
};
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 12px;
  z-index: 100;
  margin: 12px 24px;
  padding: 10px 24px;
  border-radius: var(--radius-xl);
}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.brand-icon {
  font-size: 1.8rem;
  line-height: 1;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 800;
  background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.02em;
}

.brand-tag {
  font-size: 0.65rem;
  color: var(--accent-cyan);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.25);
  padding: 4px;
  border-radius: 9999px;
  border: 1px solid var(--border-color);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  text-decoration: none;
  transition: all 0.2s ease;
  position: relative;
}

.nav-item:hover {
  color: var(--text-main);
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  color: white;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.nav-item-chat {
  color: var(--accent-cyan);
}

.pulse-dot {
  width: 7px;
  height: 7px;
  background: var(--accent-cyan);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--accent-cyan);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.7); }
  70% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(6, 182, 212, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(6, 182, 212, 0); }
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent-cyan) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.95rem;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-main);
}

.user-email {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.8rem;
}
</style>
