<template>
  <div class="flex flex-col h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
    <!-- Header -->
    <div class="flex-shrink-0 px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Travel Assistant</h2>
        <button
          @click="clearChat"
          class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 px-2 py-1 rounded transition-colors"
        >
          Clear Chat
        </button>
      </div>
    </div>

    <!-- Messages Container -->
    <div 
      ref="messagesContainer"
      class="flex-1 overflow-y-auto px-4 py-4 space-y-4 custom-scrollbar bg-white dark:bg-gray-800"
    >
      <div
        v-for="message in messages"
        :key="message.id"
        class="animate-slide-up"
      >
        <!-- User Message -->
        <div v-if="message.sender === 'user'" class="flex justify-end">
          <div class="max-w-xs lg:max-w-md">
            <div class="bg-primary-500 text-white rounded-lg px-4 py-2 shadow-sm">
              <p class="text-sm">{{ message.content }}</p>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">
              {{ formatTime(message.timestamp) }}
            </p>
          </div>
        </div>

        <!-- Bot Message -->
        <div v-else class="flex justify-start">
          <div class="max-w-xs lg:max-w-md">
            <div class="bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg px-4 py-2 shadow-sm">
              <p class="text-sm">{{ message.content }}</p>
              
              <!-- Options Menu -->
              <div v-if="message.options && message.options.length > 0" class="mt-3">
                <!-- For cuisine selection (multiple choice) -->
                <div v-if="isCuisineSelection(message)" class="space-y-2">
                  <label
                    v-for="(option, index) in message.options"
                    :key="index"
                    class="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600 p-1 rounded"
                  >
                    <input
                      type="checkbox"
                      :value="option"
                      v-model="selectedOptions"
                      class="rounded border-gray-300 dark:border-gray-600 text-primary-500 shadow-sm focus:border-primary-500 focus:ring focus:ring-primary-500 focus:ring-opacity-50 dark:bg-gray-700"
                    >
                    <span class="text-sm text-gray-700 dark:text-gray-300">{{ option }}</span>
                  </label>
                  <button
                    v-if="selectedOptions.length > 0"
                    @click="submitSelectedOptions"
                    :disabled="isLoading"
                    class="mt-2 w-full bg-primary-500 text-white text-sm px-3 py-1.5 rounded-md hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Submit Selection
                  </button>
                </div>

                <!-- For all other options (single choice) -->
                <div v-else class="space-y-2">
                  <label
                    v-for="(option, index) in message.options"
                    :key="index"
                    class="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600 p-1 rounded"
                  >
                    <input
                      type="radio"
                      :value="option"
                      v-model="selectedOption"
                      class="border-gray-300 dark:border-gray-600 text-primary-500 shadow-sm focus:border-primary-500 focus:ring focus:ring-primary-500 focus:ring-opacity-50 dark:bg-gray-700"
                    >
                    <span class="text-sm text-gray-700 dark:text-gray-300">{{ option }}</span>
                  </label>
                  <button
                    v-if="selectedOption"
                    @click="submitSingleOption"
                    :disabled="isLoading"
                    class="mt-2 w-full bg-primary-500 text-white text-sm px-3 py-1.5 rounded-md hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Submit
                  </button>
                </div>
              </div>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {{ formatTime(message.timestamp) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="flex justify-start">
        <div class="bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-2">
          <div class="flex items-center space-x-1">
            <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
            <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="px-4 py-2 bg-red-50 dark:bg-red-900/30 border-t border-red-200 dark:border-red-800">
      <p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
    </div>

    <!-- Input Area -->
    <div class="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800">
      <div class="flex space-x-2">
        <input
          v-model="inputMessage"
          @keypress.enter="handleSendMessage"
          :disabled="isLoading"
          type="text"
          placeholder="Type your message..."
          class="flex-1 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
        >
        <button
          @click="handleSendMessage"
          :disabled="isLoading || !inputMessage.trim()"
          class="bg-primary-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue';
import type { Message } from '../types';

interface Props {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

interface Emits {
  (e: 'send-message', message: string): void;
  (e: 'clear-chat'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const inputMessage = ref('');
const selectedOptions = ref<string[]>([]); // For cuisine selection (multiple choice)
const selectedOption = ref<string>(''); // For all other options (single choice)
const messagesContainer = ref<HTMLElement>();

// Helper function to determine if we're in cuisine selection mode
const isCuisineSelection = (message: Message) => {
  // Check if the message is asking about cuisines
  return message.content.toLowerCase().includes('cuisine') || 
         message.content.toLowerCase().includes('food type') ||
         message.options?.some(opt => opt.toLowerCase().includes('cuisine'));
};

const handleSendMessage = () => {
  if (inputMessage.value.trim() && !props.isLoading) {
    emit('send-message', inputMessage.value.trim());
    inputMessage.value = '';
  }
};

const submitSelectedOptions = () => {
  if (selectedOptions.value.length > 0) {
    const message = selectedOptions.value.join(', ');
    emit('send-message', message);
    selectedOptions.value = [];
  }
};

const submitSingleOption = () => {
  if (selectedOption.value) {
    emit('send-message', selectedOption.value);
    selectedOption.value = '';
  }
};

const clearChat = () => {
  emit('clear-chat');
};

const formatTime = (date: Date | undefined): string => {
  if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
    return '--:--';
  }
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// Auto-scroll to bottom when new messages arrive
watch(() => props.messages.length, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
});

// Reset selections when messages change
watch(() => props.messages, () => {
  selectedOptions.value = [];
  selectedOption.value = '';
}, { deep: true });
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

.animate-slide-up {
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>