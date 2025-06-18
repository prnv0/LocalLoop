<template>
  <div class="h-screen bg-gray-50 dark:bg-gray-900 flex flex-col transition-colors duration-200">
    <!-- Header -->
    <header class="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
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
          <h1 class="text-xl font-bold text-gray-900 dark:text-white">LocalLoop</h1>
        </div>
        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-500 dark:text-gray-400">
            Chat-driven itinerary planning
          </div>
          <!-- Dark mode toggle button -->
          <button
            @click="darkMode.toggleDarkMode"
            class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            :title="darkMode.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          >
            <!-- Sun icon for dark mode -->
            <svg
              v-if="darkMode.isDark"
              class="w-5 h-5 text-gray-400 hover:text-gray-200"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
              />
            </svg>
            <!-- Moon icon for light mode -->
            <svg
              v-else
              class="w-5 h-5 text-gray-600 hover:text-gray-900"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
              />
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 flex overflow-hidden max-w-7xl mx-auto w-full">
      <!-- Mobile Layout (Stack) -->
      <div class="flex flex-col md:hidden w-full">
        <!-- Mobile Tab Selector -->
        <div class="flex bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
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
            <span v-if="chat.messages.value.length > 1" class="ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-primary-500 rounded-full">
              {{ chat.messages.value.length - 1 }}
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
            <span v-if="chat.currentItinerary.value && chat.currentItinerary.value.ordered_places.length > 0" 
                  class="ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-green-500 rounded-full">
              {{ chat.currentItinerary.value.ordered_places.length }}
            </span>
          </button>
        </div>

        <!-- Mobile Content -->
        <div class="flex-1 overflow-hidden">
          <ChatPane
            v-show="mobileView === 'chat'"
            :messages="chat.messages.value"
            :is-loading="chat.isLoading.value"
            :error="chat.error.value"
            @send-message="handleSendMessage"
            @clear-chat="chat.clearChat"
            class="h-full"
          />
          <ItineraryView
            v-show="mobileView === 'itinerary'"
            :current-itinerary="chat.currentItinerary.value"
            @remove-stop="chat.removeItineraryStop"
            @edit-stop="handleEditStop"
            @add-stop="handleAddStop"
            class="h-full"
          />
        </div>
      </div>

      <!-- Desktop Layout (Side by Side) -->
      <div class="hidden md:flex w-full">
        <!-- Chat Pane (40%) -->
        <div class="w-2/5 min-w-0">
          <ChatPane
            :messages="chat.messages.value"
            :is-loading="chat.isLoading.value"
            :error="chat.error.value"
            @send-message="handleSendMessage"
            @clear-chat="chat.clearChat"
            class="h-full"
          />
        </div>

        <!-- Itinerary View (60%) -->
        <div class="w-3/5 min-w-0">
          <ItineraryView
            :current-itinerary="chat.currentItinerary.value"
            @remove-stop="chat.removeItineraryStop"
            @edit-stop="handleEditStop"
            @add-stop="handleAddStop"
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
import { useDarkMode } from './composables/useDarkMode';

const chat = useChat();
const darkMode = useDarkMode();
const mobileView = ref<'chat' | 'itinerary'>('chat');

const handleSendMessage = async (message: string): Promise<void> => {
  await chat.sendMessage(message);
  // Switch to itinerary view on mobile after sending message
  if (window.innerWidth < 768) {
    setTimeout(() => {
      if (chat.currentItinerary.value && chat.currentItinerary.value.ordered_places.length > 0) {
        mobileView.value = 'itinerary';
      }
    }, 1000);
  }
};

const handleEditStop = async (stopId: string, locationName: string, placeType?: string): Promise<void> => {
  // Find the stop number in the itinerary
  const stopIndex = chat.currentItinerary.value?.ordered_places.findIndex(place => place.id === stopId);
  if (stopIndex !== undefined && stopIndex !== -1) {
    const ordinal = getOrdinalSuffix(stopIndex + 1);
    const message = placeType 
      ? `replace ${stopIndex + 1}${ordinal} stop with ${locationName} as a ${placeType}`
      : `replace ${stopIndex + 1}${ordinal} stop with ${locationName}`;
    await chat.sendMessage(message);
  }
};

const handleAddStop = async (locationName: string, placeType?: string): Promise<void> => {
  const message = placeType 
    ? `add ${locationName} as a ${placeType}`
    : `add ${locationName}`;
  await chat.sendMessage(message);
};

const getOrdinalSuffix = (n: number): string => {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return s[(v - 20) % 10] || s[v] || s[0];
};
</script>