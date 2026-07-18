<template>
  <div class="login-wrapper">
    <div class="login-card glass-panel">
      <!-- Brand header -->
      <div class="login-header">
        <div class="brand-badge">🧞‍♂️</div>
        <h2>Welcome to ShopGenie</h2>
        <p>AI-First Conversational E-Commerce Platform</p>
      </div>

      <!-- Quick Fill Test Accounts -->
      <div class="quick-accounts">
        <span class="quick-title">Quick Test Accounts (Click to Fill):</span>
        <div class="accounts-grid">
          <button @click="fillCredentials('john@test.com', '123456')" class="account-btn" :class="{ selected: email === 'john@test.com' }">
            <div class="acc-name">John</div>
            <div class="acc-email">john@test.com</div>
          </button>
          <button @click="fillCredentials('alice@test.com', 'password')" class="account-btn" :class="{ selected: email === 'alice@test.com' }">
            <div class="acc-name">Alice</div>
            <div class="acc-email">alice@test.com</div>
          </button>
          <button @click="fillCredentials('bob@test.com', 'abc123')" class="account-btn" :class="{ selected: email === 'bob@test.com' }">
            <div class="acc-name">Bob</div>
            <div class="acc-email">bob@test.com</div>
          </button>
        </div>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="login-form">
        <div v-if="error" class="error-alert">
          <i class="fa-solid fa-circle-exclamation"></i>
          <span>{{ error }}</span>
        </div>

        <div class="form-group">
          <label for="email">Email Address</label>
          <div class="input-with-icon">
            <i class="fa-solid fa-envelope"></i>
            <input 
              id="email" 
              v-model="email" 
              type="email" 
              placeholder="john@test.com" 
              required 
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <div class="input-with-icon">
            <i class="fa-solid fa-lock"></i>
            <input 
              id="password" 
              v-model="password" 
              type="password" 
              placeholder="123456" 
              required 
            />
          </div>
        </div>

        <button type="submit" class="btn btn-primary login-btn" :disabled="loading">
          <i v-if="loading" class="fa-solid fa-spinner fa-spin"></i>
          <span v-else>Sign In to ShopGenie</span>
        </button>
      </form>

      <div class="login-footer">
        <p>Instant JWT Generation & Tools Enabled</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

const router = useRouter();
const { login, state: authState } = useAuthStore();

const email = ref('john@test.com');
const password = ref('123456');
const loading = ref(false);
const error = ref(null);

const fillCredentials = (userEmail, userPass) => {
  email.value = userEmail;
  password.value = userPass;
};

const handleLogin = async () => {
  loading.value = true;
  error.value = null;

  const success = await login(email.value, password.value);
  loading.value = false;

  if (success) {
    router.push('/chat');
  } else {
    error.value = authState.error || 'Invalid credentials. Please try again.';
  }
};
</script>

<style scoped>
.login-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 440px;
  padding: 36px 32px;
  border-radius: var(--radius-xl);
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.brand-badge {
  font-size: 3rem;
  margin-bottom: 8px;
}

.login-header h2 {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-main);
}

.login-header p {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.quick-accounts {
  margin-bottom: 24px;
}

.quick-title {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
  display: block;
  margin-bottom: 8px;
}

.accounts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.account-btn {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-color);
  padding: 8px;
  border-radius: var(--radius-md);
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.account-btn:hover, .account-btn.selected {
  background: var(--primary-light);
  border-color: var(--primary);
}

.acc-name {
  font-weight: 700;
  font-size: 0.8rem;
  color: var(--text-main);
}

.acc-email {
  font-size: 0.65rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.error-alert {
  background: rgba(244, 63, 94, 0.15);
  border: 1px solid rgba(244, 63, 94, 0.3);
  color: var(--accent-rose);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: 0.82rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-with-icon i {
  position: absolute;
  left: 14px;
  color: var(--text-subtle);
  font-size: 0.9rem;
}

.input-with-icon input {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px 14px 12px 40px;
  color: var(--text-main);
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s ease;
}

.input-with-icon input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.login-btn {
  width: 100%;
  padding: 14px;
  margin-top: 8px;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 0.72rem;
  color: var(--text-subtle);
}
</style>
