import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('shopgenie_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const authService = {
  login: async (email, password) => {
    const response = await api.post('/login', { email, password });
    return response.data;
  }
};

export const orderService = {
  getOrders: async () => {
    const response = await api.get('/orders');
    return response.data;
  },
  createOrder: async (product, quantity = 1, amount = null) => {
    const response = await api.post('/orders', { product, quantity, amount });
    return response.data;
  }
};

export const paymentService = {
  getPayments: async () => {
    const response = await api.get('/payments');
    return response.data;
  },
  payOrder: async (order_id, method = 'Visa') => {
    const response = await api.post('/payment', { order_id, method });
    return response.data;
  }
};

export const feedbackService = {
  getFeedback: async () => {
    const response = await api.get('/feedback');
    return response.data;
  },
  submitFeedback: async (message, order_id = null) => {
    const response = await api.post('/feedback', { message, order_id });
    return response.data;
  }
};

export const chatService = {
  sendMessage: async (message, userId = null) => {
    const response = await api.post('/chat', { message, user_id: userId });
    return response.data;
  }
};

export default api;
