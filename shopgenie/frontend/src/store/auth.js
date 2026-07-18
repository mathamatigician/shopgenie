import { reactive, computed } from 'vue';
import { authService } from '../services/api';

const state = reactive({
  token: localStorage.getItem('shopgenie_token') || null,
  user: JSON.parse(localStorage.getItem('shopgenie_user') || 'null'),
  loading: false,
  error: null
});

export const useAuthStore = () => {
  const isAuthenticated = computed(() => !!state.token);

  const login = async (email, password) => {
    state.loading = true;
    state.error = null;
    try {
      const data = await authService.login(email, password);
      state.token = data.access_token;
      state.user = data.user;
      localStorage.setItem('shopgenie_token', data.access_token);
      localStorage.setItem('shopgenie_user', JSON.stringify(data.user));
      state.loading = false;
      return true;
    } catch (err) {
      state.error = err.response?.data?.detail || 'Login failed. Check credentials.';
      state.loading = false;
      return false;
    }
  };

  const logout = () => {
    state.token = null;
    state.user = null;
    localStorage.removeItem('shopgenie_token');
    localStorage.removeItem('shopgenie_user');
  };

  return {
    state,
    isAuthenticated,
    login,
    logout
  };
};
