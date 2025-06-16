export interface Leg {
  start_address: string;
  end_address: string;
  distance: string;
  duration: string;
}

export interface Itinerary {
  legs: Leg[];
  ordered_places: Array<{
    name: string;
    address: string;
    rating?: number;
    // ... other place properties
  }>;
  summary?: string;
} 