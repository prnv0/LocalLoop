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

export interface Leg {
  start_address: string;
  end_address: string;
  distance: string;
  duration: string;
}

export interface Place {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  rating?: number;
}

export interface Itinerary {
  legs: Leg[];
  ordered_places: Place[];
  summary?: string;
}

export interface ChatResponse {
  session_id: string;
  reply?: string;
  options?: string[];
  itinerary?: Itinerary;
}

export interface ApiRequest {
  session_id: string;
  message: string;
}

export type ViewMode = 'map' | 'list';