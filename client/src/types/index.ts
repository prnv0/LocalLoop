export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  options?: string[];
}

export interface ItineraryStop {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  rating?: number;
  travelTime?: string;
}

export interface Itinerary {
  id: string;
  title: string;
  stops: ItineraryStop[];
  totalDuration?: string;
}

export interface ChatResponse {
  message?: string;
  options?: string[];
  itinerary?: Itinerary;
}

export interface ApiRequest {
  session_id: string;
  message: string;
}

export type ViewMode = 'map' | 'list';