<template>
  <div class="chat-page">
    <div class="page-header text-center">
      <h1 class="page-title">Conversational Shopping</h1>
      <p class="page-subtitle">Zero navigation. Complete your shopping entirely through natural dialogue.</p>
    </div>

    <!-- Chat Window Container -->
    <ChatWindow />

    <!-- Features & Target Accessibility Info Cards -->
    <div class="features-row">
      <div class="feature-card glass-panel">
        <div class="f-icon">👴</div>
        <h4>Elderly & Accessibility Friendly</h4>
        <p>Speak directly using the microphone button with natural voice feedback.</p>
      </div>

      <div class="feature-card glass-panel">
        <div class="f-icon">⚡</div>
        <h4>AI Tool Calling</h4>
        <p>Automated execution for order creation, payments, and sentiment analysis.</p>
      </div>

      <div class="feature-card glass-panel">
        <div class="f-icon">🎯</div>
        <h4>Zero Page Navigation</h4>
        <p>No multi-page checkout, complex search filters, or forms required.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import ChatWindow from '../components/ChatWindow.vue';
</script>

<style scoped>
.chat-page {
  max-width: 1100px;
  margin: 20px auto;
  padding: 0 20px 40px;
}

.text-center {
  text-align: center;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--text-main);
}

.page-subtitle {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-bottom: 20px;
}

.features-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.feature-card {
  padding: 20px;
  text-align: center;
}

.f-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.feature-card h4 {
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 6px;
  color: var(--text-main);
}

.feature-card p {
  font-size: 0.8rem;
  color: var(--text-muted);
}
</style>
