import { ref, reactive } from 'vue';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import type { Message, ChatResponse, ApiRequest, Itinerary } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export function useChat() {
  const sessionId = ref(uuidv4());
  const messages = ref<Message[]>([]);
  const currentItinerary = ref<Itinerary | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Add initial welcome message
  const addWelcomeMessage = () => {
    messages.value.push({
      id: uuidv4(),
      content: "Hello! I'm your travel planning assistant. Where would you like to go and when?",
      sender: 'bot',
      timestamp: new Date()
    });
  };

  const addMessage = (content: string, sender: 'user' | 'bot', options?: string[]) => {
    const message: Message = {
      id: uuidv4(),
      content,
      sender,
      timestamp: new Date(),
      options
    };
    messages.value.push(message);
    return message;
  };

  const sendMessage = async (content: string): Promise<void> => {
    if (!content.trim()) return;

    // Clear any previous errors
    error.value = null;
    
    // Add user message
    addMessage(content, 'user');
    
    // Set loading state
    isLoading.value = true;

    try {
      const request: ApiRequest = {
        session_id: sessionId.value,
        message: content
      };

      const response = await axios.post<ChatResponse>(`${API_BASE_URL}/chat`, request);
      const data = response.data;

      // Add bot response
      if (data.message) {
        addMessage(data.message, 'bot', data.options);
      }

      // Update itinerary if provided
      if (data.itinerary) {
        currentItinerary.value = data.itinerary;
      }

    } catch (err) {
      console.error('Chat API error:', err);
      error.value = 'Failed to send message. Please check if the server is running.';
      addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    } finally {
      isLoading.value = false;
    }
  };

  const removeItineraryStop = (stopId: string) => {
    if (currentItinerary.value) {
      currentItinerary.value.stops = currentItinerary.value.stops.filter(
        stop => stop.id !== stopId
      );
    }
  };

  const clearChat = () => {
    messages.value = [];
    currentItinerary.value = null;
    sessionId.value = uuidv4();
    addWelcomeMessage();
  };

  // Initialize with welcome message
  addWelcomeMessage();

  return {
    sessionId: sessionId.value,
    messages,
    currentItinerary,
    isLoading,
    error,
    sendMessage,
    addMessage,
    removeItineraryStop,
    clearChat
  };
}