<template>
  <div class="h-screen bg-gray-50 flex flex-col">
    <!-- Header -->
    <header class="flex-shrink-0 bg-white border-b border-gray-200 px-4 py-3">
      <div class="flex items-center justify-between max-w-7xl mx-auto">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </div>
          <h1 class="text-xl font-bold text-gray-900">TravelPlanner AI</h1>
        </div>
        <div class="text-sm text-gray-500">
          Chat-driven itinerary planning
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 flex overflow-hidden max-w-7xl mx-auto w-full">
      <!-- Mobile Layout (Stack) -->
      <div class="flex flex-col md:hidden w-full">
        <!-- Mobile Tab Selector -->
        <div class="flex bg-white border-b border-gray-200">
          <button
            @click="mobileView = 'chat'"
            :class="[
              'flex-1 py-3 px-4 text-sm font-medium border-b-2 transition-colors',
              mobileView === 'chat'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            ]"
          >
            Chat
            <span v-if="chat.messages.length > 1" class="ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-primary-500 rounded-full">
              {{ chat.messages.length - 1 }}
            </span>
          </button>
          <button
            @click="mobileView = 'itinerary'"
            :class="[
              'flex-1 py-3 px-4 text-sm font-medium border-b-2 transition-colors',
              mobileView === 'itinerary'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            ]"
          >
            Itinerary
            <span v-if="chat.currentItinerary.value && chat.currentItinerary.value.stops.length > 0" 
                  class="ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-green-500 rounded-full">
              {{ chat.currentItinerary.value.stops.length }}
            </span>
          </button>
        </div>

        <!-- Mobile Content -->
        <div class="flex-1 overflow-hidden">
          <ChatPane
            v-show="mobileView === 'chat'"
            :messages="chat.messages"
            :is-loading="chat.isLoading"
            :error="chat.error"
            @send-message="handleSendMessage"
            @clear-chat="chat.clearChat"
            class="h-full"
          />
          <ItineraryView
            v-show="mobileView === 'itinerary'"
            :current-itinerary="chat.currentItinerary"
            @remove-stop="chat.removeItineraryStop"
            class="h-full"
          />
        </div>
      </div>

      <!-- Desktop Layout (Side by Side) -->
      <div class="hidden md:flex w-full">
        <!-- Chat Pane (40%) -->
        <div class="w-2/5 min-w-0">
          <ChatPane
            :messages="chat.messages"
            :is-loading="chat.isLoading"
            :error="chat.error"
            @send-message="handleSendMessage"
            @clear-chat="chat.clearChat"
            class="h-full"
          />
        </div>

        <!-- Itinerary View (60%) -->
        <div class="w-3/5 min-w-0">
          <ItineraryView
            :current-itinerary="chat.currentItinerary"
            @remove-stop="chat.removeItineraryStop"
            class="h-full"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ChatPane from './components/ChatPane.vue';
import ItineraryView from './components/ItineraryView.vue';
import { useChat } from './composables/useChat';

const chat = useChat();
const mobileView = ref<'chat' | 'itinerary'>('chat');

const handleSendMessage = async (message: string) => {
  await chat.sendMessage(message);
  // Switch to itinerary view on mobile after sending message
  if (window.innerWidth < 768) {
    setTimeout(() => {
      if (chat.currentItinerary.value && chat.currentItinerary.value.stops.length > 0) {
        mobileView.value = 'itinerary';
      }
    }, 1000);
  }
};
</script>