import { ref } from 'vue';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import type { Message, ChatResponse, ApiRequest, Itinerary } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export function useChat() {
  const messages = ref<Message[]>([]);
  const currentItinerary = ref<Itinerary | null>(null);
  const sessionId = ref<string | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Send a message with no session id to initiate chat
  async function initSession() {
    let message = "Choose your trip type:";
    const {session_id, reply, options} = await axios.post<ChatResponse>(`${API_BASE_URL}/chat`, {message: message}).then(r=>r.data);
    sessionId.value = session_id;
    console.log(message, reply, options);
    addMessage(message , 'bot', options);
  }
  initSession();

  // Add initial welcome message
  const addWelcomeMessage = () => {
    messages.value.push({
      id: uuidv4(),
      content: "Hello! I'm your travel planning assistant.",
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
    if (!content.trim() || !sessionId.value) return;

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
      console.log(data);

      // Add bot response
      if (data.reply) {
        addMessage(data.reply, 'bot', data.options);
      }

      // Update itinerary if provided (but don't display in chat)
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
      // Remove the place and its corresponding leg
      const index = currentItinerary.value.ordered_places.findIndex(place => place.id === stopId);
      if (index !== -1) {
        currentItinerary.value.ordered_places.splice(index, 1);
        // Remove the corresponding leg if it exists
        if (currentItinerary.value.legs[index]) {
          currentItinerary.value.legs.splice(index, 1);
        }
      }
    }
  };

  const clearChat = () => {
    messages.value = [];
    currentItinerary.value = null;
    sessionId.value = null;
    initSession();
  };

  // Initialize with welcome message
  addWelcomeMessage();

  return {
    sessionId,
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