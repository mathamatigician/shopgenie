<template>
  <div class="chat-container glass-panel">
    <!-- Header -->
    <div class="chat-header">
      <div class="header-info">
        <div class="ai-avatar">🧞‍♂️</div>
        <div>
          <h3 class="header-title">ShopGenie Assistant</h3>
          <p class="header-subtitle">Speak or type naturally to shop, pay & request support</p>
        </div>
      </div>
      <div class="header-controls">
        <button 
          @click="toggleTts" 
          class="control-btn" 
          :class="{ active: ttsEnabled }" 
          :title="ttsEnabled ? 'Mute Speech Output' : 'Enable Speech Output'"
        >
          <i :class="ttsEnabled ? 'fa-solid fa-volume-high' : 'fa-solid fa-volume-xmark'"></i>
        </button>
        <button @click="clearChat" class="control-btn" title="Clear Conversation">
          <i class="fa-solid fa-rotate-right"></i>
        </button>
      </div>
    </div>

    <!-- Messages Container -->
    <div class="messages-list" ref="messagesListRef">
      <div v-if="messages.length === 0" class="welcome-box">
        <div class="welcome-icon">💬</div>
        <h4>Start Shopping with Conversation!</h4>
        <p>No screens or standard search needed. Try clicking one of the sample prompt chips below or speak directly!</p>
      </div>

      <div 
        v-for="(msg, idx) in messages" 
        :key="idx" 
        class="message-wrapper" 
        :class="msg.sender"
      >
        <div class="msg-avatar">
          <span v-if="msg.sender === 'user'">👤</span>
          <span v-else>🧞‍♂️</span>
        </div>

        <div class="msg-bubble">
          <!-- Tool Execution Badge if tool was executed -->
          <div v-if="msg.tool_called" class="tool-badge">
            <i class="fa-solid fa-bolt"></i>
            <span>Tool Called: <strong>{{ msg.tool_called }}</strong></span>
          </div>

          <!-- Message Text -->
          <div class="msg-text" v-html="formatMarkdown(msg.text)"></div>

          <!-- Tool Data View Details if available -->
          <div v-if="msg.data" class="tool-details-card">
            <!-- Order created card -->
            <div v-if="msg.tool_called === 'create_order'" class="mini-card">
              <span class="mini-label">Order Details:</span>
              <div class="mini-flex">
                <span>#{{ msg.data.order?.order_id }} {{ msg.data.order?.product }} (x{{ msg.data.order?.quantity }})</span>
                <span class="badge badge-pending">₹{{ msg.data.order?.amount }}</span>
              </div>
            </div>

            <!-- Payment card -->
            <div v-if="msg.tool_called === 'pay_order'" class="mini-card">
              <span class="mini-label">Payment Receipt:</span>
              <div class="mini-flex">
                <span>ID: {{ msg.data.payment?.payment_id }}</span>
                <span class="badge badge-paid">PAID ₹{{ msg.data.payment?.amount }}</span>
              </div>
            </div>

            <!-- Recommendations list -->
            <div v-if="msg.tool_called === 'recommend_products' && msg.data.recommendations" class="recs-grid">
              <div v-for="item in msg.data.recommendations" :key="item.id" class="rec-item">
                <span class="rec-emoji">{{ item.image || '📦' }}</span>
                <div class="rec-info">
                  <div class="rec-name">{{ item.name }}</div>
                  <div class="rec-price">₹{{ item.price }}</div>
                </div>
                <button @click="sendPrompt(`Order a ${item.name}`)" class="btn btn-secondary btn-xs">
                  Buy
                </button>
              </div>
            </div>
          </div>

          <div class="msg-time">{{ msg.time }}</div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="loading" class="message-wrapper assistant">
        <div class="msg-avatar">🧞‍♂️</div>
        <div class="msg-bubble loading-bubble">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>

    <!-- Quick Prompt Suggestions Chips -->
    <div class="prompt-chips">
      <span class="chips-label"><i class="fa-solid fa-lightbulb"></i> Try asking:</span>
      <button @click="sendPrompt('I want another keyboard')" class="chip">
        ⌨️ I want another keyboard
      </button>
      <button @click="sendPrompt('Pay for my latest order')" class="chip">
        💳 Pay for my latest order
      </button>
      <button @click="sendPrompt('Packaging was poor for order 101')" class="chip">
        📦 Packaging was poor
      </button>
      <button @click="sendPrompt('Recommend laptop bags')" class="chip">
        🎒 Recommend laptop bags
      </button>
      <button @click="sendPrompt('Show my orders')" class="chip">
        📋 Show my orders
      </button>
    </div>

    <!-- Input Bar -->
    <div class="chat-input-bar">
      <!-- Voice Input Microphone Button -->
      <button 
        @click="toggleListening" 
        class="mic-btn" 
        :class="{ listening: isListening }"
        :title="isListening ? 'Listening... Speak now' : 'Voice Input (Accessibility)'"
      >
        <i :class="isListening ? 'fa-solid fa-microphone-slash' : 'fa-solid fa-microphone'"></i>
      </button>

      <input 
        v-model="inputQuery" 
        @keyup.enter="handleSend" 
        type="text" 
        placeholder="Type or speak e.g. 'Order another mouse', 'Pay for latest order'..."
        class="chat-input"
        :disabled="loading"
      />

      <button @click="handleSend" class="send-btn" :disabled="!inputQuery.trim() || loading">
        <i class="fa-solid fa-paper-plane"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { chatService } from '../services/api';
import { useAuthStore } from '../store/auth';

const { state: authState } = useAuthStore();
const messages = ref([]);
const inputQuery = ref('');
const loading = ref(false);
const messagesListRef = ref(null);

const ttsEnabled = ref(false);
const isListening = ref(false);
let recognition = null;

const emit = defineEmits(['order-updated']);

onMounted(() => {
  // Add initial welcoming assistant message
  const userName = authState.user?.name || 'there';
  messages.value.push({
    sender: 'assistant',
    text: `Hello ${userName}! 👋 Welcome to **ShopGenie**. How can I assist your shopping today? You can ask to order items, make payments, or give feedback.`,
    time: getCurrentTime()
  });

  // Setup Web Speech API if supported
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      inputQuery.value = transcript;
      isListening.value = false;
      handleSend();
    };

    recognition.onerror = () => {
      isListening.value = false;
    };

    recognition.onend = () => {
      isListening.value = false;
    };
  }
});

const getCurrentTime = () => {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesListRef.value) {
      messagesListRef.value.scrollTop = messagesListRef.value.scrollHeight;
    }
  });
};

const handleSend = async () => {
  const text = inputQuery.value.trim();
  if (!text || loading.value) return;

  // Add User Message
  messages.value.push({
    sender: 'user',
    text: text,
    time: getCurrentTime()
  });

  inputQuery.value = '';
  loading.value = true;
  scrollToBottom();

  try {
    const res = await chatService.sendMessage(text, authState.user?.id);
    loading.value = false;

    messages.value.push({
      sender: 'assistant',
      text: res.reply,
      tool_called: res.tool_called,
      tool_output: res.tool_output,
      data: res.data,
      time: getCurrentTime()
    });

    if (ttsEnabled.value) {
      speak(res.reply);
    }

    emit('order-updated');
    scrollToBottom();
  } catch (err) {
    loading.value = false;
    messages.value.push({
      sender: 'assistant',
      text: "Sorry, I couldn't process that request right now. Please try again.",
      time: getCurrentTime()
    });
    scrollToBottom();
  }
};

const sendPrompt = (text) => {
  inputQuery.value = text;
  handleSend();
};

const clearChat = () => {
  messages.value = [{
    sender: 'assistant',
    text: "Conversation cleared. How can I help you next?",
    time: getCurrentTime()
  }];
};

const toggleListening = () => {
  if (!recognition) {
    alert("Speech recognition is not supported in this browser.");
    return;
  }
  if (isListening.value) {
    recognition.stop();
    isListening.value = false;
  } else {
    isListening.value = true;
    recognition.start();
  }
};

const toggleTts = () => {
  ttsEnabled.value = !ttsEnabled.value;
  if (!ttsEnabled.value && window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
};

const speak = (text) => {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    // Strip markdown formatting for cleaner speech
    const cleanText = text.replace(/[*_~`#]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    window.speechSynthesis.speak(utterance);
  }
};

const formatMarkdown = (text) => {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br/>');
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 640px;
  max-width: 900px;
  margin: 0 auto;
  overflow: hidden;
  border-radius: var(--radius-xl);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(15, 23, 42, 0.8);
  border-bottom: 1px solid var(--border-color);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-avatar {
  font-size: 2rem;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
}

.header-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
}

.header-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.header-controls {
  display: flex;
  gap: 8px;
}

.control-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.control-btn:hover, .control-btn.active {
  background: var(--primary-light);
  color: var(--primary);
  border-color: var(--border-glow);
}

.messages-list {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: rgba(10, 15, 26, 0.4);
}

.welcome-box {
  text-align: center;
  padding: 30px;
  margin: auto;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed var(--border-color);
  border-radius: var(--radius-lg);
}

.welcome-icon {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.welcome-box h4 {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.welcome-box p {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.message-wrapper {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-wrapper.assistant {
  align-self: flex-start;
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.msg-bubble {
  background: rgba(30, 41, 67, 0.8);
  border: 1px solid var(--border-color);
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  font-size: 0.92rem;
  color: var(--text-main);
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.message-wrapper.user .msg-bubble {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  border-color: transparent;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-wrapper.assistant .msg-bubble {
  border-bottom-left-radius: 4px;
}

.tool-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(6, 182, 212, 0.15);
  color: var(--accent-cyan);
  border: 1px solid rgba(6, 182, 212, 0.3);
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.msg-time {
  font-size: 0.68rem;
  color: var(--text-subtle);
  margin-top: 6px;
  text-align: right;
}

.tool-details-card {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.mini-card {
  background: rgba(0, 0, 0, 0.25);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  font-size: 0.82rem;
}

.mini-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 700;
  display: block;
  margin-bottom: 4px;
}

.mini-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
  margin-top: 6px;
}

.rec-item {
  background: rgba(0, 0, 0, 0.3);
  padding: 8px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--border-color);
}

.rec-emoji {
  font-size: 1.4rem;
}

.rec-info {
  flex: 1;
  overflow: hidden;
}

.rec-name {
  font-weight: 700;
  font-size: 0.78rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rec-price {
  font-size: 0.72rem;
  color: var(--accent-emerald);
}

.btn-xs {
  padding: 3px 8px;
  font-size: 0.7rem;
}

.prompt-chips {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(15, 23, 42, 0.6);
  border-top: 1px solid var(--border-color);
  overflow-x: auto;
  white-space: nowrap;
}

.chips-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.chip {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  padding: 5px 12px;
  border-radius: 9999px;
  font-size: 0.78rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chip:hover {
  background: var(--primary-light);
  border-color: var(--border-glow);
  transform: translateY(-1px);
}

.chat-input-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  background: rgba(15, 23, 42, 0.95);
  border-top: 1px solid var(--border-color);
}

.chat-input {
  flex: 1;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid var(--border-color);
  border-radius: 9999px;
  padding: 12px 20px;
  color: var(--text-main);
  font-size: 0.92rem;
  outline: none;
  transition: border-color 0.2s ease;
}

.chat-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.mic-btn, .send-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.mic-btn {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-muted);
}

.mic-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.mic-btn.listening {
  background: var(--accent-rose);
  color: white;
  animation: pulse 1s infinite;
}

.send-btn {
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: white;
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Typing Dots */
.loading-bubble {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 14px 20px;
}

.dot {
  width: 8px;
  height: 8px;
  background: var(--text-muted);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}
</style>
