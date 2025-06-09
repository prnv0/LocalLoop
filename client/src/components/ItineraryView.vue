<template>
  <div class="flex flex-col h-full bg-white">
    <!-- Header with View Toggle -->
    <div class="flex-shrink-0 px-4 py-3 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">
          {{ currentItinerary?.title || 'Your Itinerary' }}
        </h2>
        <div class="flex bg-gray-100 rounded-lg p-1">
          <button
            @click="viewMode = 'list'"
            :class="[
              'px-3 py-1 text-sm font-medium rounded-md transition-colors',
              viewMode === 'list' 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            List
          </button>
          <button
            @click="viewMode = 'map'"
            :class="[
              'px-3 py-1 text-sm font-medium rounded-md transition-colors',
              viewMode === 'map' 
                ? 'bg-white text-gray-900 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            Map
          </button>
        </div>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-hidden">
      <!-- Empty State -->
      <div v-if="!currentItinerary || !currentItinerary.stops || currentItinerary.stops.length === 0" 
           class="flex items-center justify-center h-full text-center p-8">
        <div class="max-w-sm">
          <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">No Itinerary Yet</h3>
          <p class="text-gray-500">Start chatting to create your travel itinerary!</p>
        </div>
      </div>

      <!-- List View -->
      <div v-else-if="viewMode === 'list'" class="h-full overflow-y-auto custom-scrollbar">
        <div class="p-4 space-y-4">
          <div
            v-for="(stop, index) in currentItinerary.stops"
            :key="stop.id"
            class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors animate-fade-in"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-2 mb-2">
                  <span class="inline-flex items-center justify-center w-6 h-6 bg-primary-500 text-white text-sm font-medium rounded-full">
                    {{ index + 1 }}
                  </span>
                  <h3 class="text-lg font-medium text-gray-900">{{ stop.name }}</h3>
                  <div v-if="stop.rating" class="flex items-center">
                    <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                    <span class="ml-1 text-sm text-gray-600">{{ stop.rating }}</span>
                  </div>
                </div>
                <p class="text-gray-600 text-sm mb-2">{{ stop.address }}</p>
                <div v-if="stop.travelTime && index > 0" class="text-sm text-gray-500">
                  🚗 {{ stop.travelTime }} from previous stop
                </div>
              </div>
              <button
                @click="removeStop(stop.id)"
                class="ml-4 text-gray-400 hover:text-red-500 transition-colors"
                title="Remove stop"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Map View -->
      <div v-else class="h-full">
        <div ref="mapContainer" class="w-full h-full bg-gray-100 flex items-center justify-center">
          <div class="text-center">
            <div class="w-16 h-16 mx-auto mb-4 bg-white rounded-full flex items-center justify-center shadow-sm">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3"/>
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">Map View</h3>
            <p class="text-gray-500">Interactive map will be displayed here</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Footer -->
    <div v-if="currentItinerary && currentItinerary.stops && currentItinerary.stops.length > 0" 
         class="flex-shrink-0 border-t border-gray-200 px-4 py-3 bg-gray-50">
      <div class="flex items-center justify-between text-sm">
        <span class="text-gray-600">
          {{ currentItinerary.stops.length }} stop{{ currentItinerary.stops.length > 1 ? 's' : '' }}
        </span>
        <span v-if="currentItinerary.totalDuration" class="text-gray-600">
          Total: {{ currentItinerary.totalDuration }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import L from 'leaflet';
import type { Itinerary, ViewMode } from '../types';

interface Props {
  currentItinerary: Itinerary | null;
}

interface Emits {
  (e: 'remove-stop', stopId: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const viewMode = ref<ViewMode>('list');
const mapContainer = ref<HTMLElement>();
let map: L.Map | null = null;
let markers: L.Marker[] = [];

const removeStop = (stopId: string) => {
  emit('remove-stop', stopId);
};

const initializeMap = () => {
  if (!mapContainer.value) return;

  try {
    map = L.map(mapContainer.value).setView([40.7128, -74.0060], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);
  } catch (error) {
    console.error('Error initializing map:', error);
  }
};

const updateMapMarkers = () => {
  if (!map || !props.currentItinerary || !props.currentItinerary.stops) return;

  // Clear existing markers
  markers.forEach(marker => map?.removeLayer(marker));
  markers = [];

  const stops = props.currentItinerary.stops;
  if (stops.length === 0) return;

  // Add markers for each stop
  stops.forEach((stop, index) => {
    const marker = L.marker([stop.lat, stop.lng])
      .addTo(map!)
      .bindPopup(`
        <div class="p-2">
          <h3 class="font-medium">${index + 1}. ${stop.name}</h3>
          <p class="text-sm text-gray-600">${stop.address}</p>
          ${stop.rating ? `<p class="text-sm">⭐ ${stop.rating}</p>` : ''}
        </div>
      `);
    markers.push(marker);
  });

  // Draw polyline connecting stops
  if (stops.length > 1) {
    const coordinates = stops.map(stop => [stop.lat, stop.lng] as [number, number]);
    L.polyline(coordinates, { color: '#3b82f6', weight: 3 }).addTo(map!);
  }

  // Fit map to show all markers
  const group = new (L as any).featureGroup(markers);
  map!.fitBounds(group.getBounds().pad(0.1));
};

// Watch for itinerary changes
watch(() => props.currentItinerary, () => {
  if (viewMode.value === 'map') {
    updateMapMarkers();
  }
}, { deep: true });

// Watch for view mode changes
watch(viewMode, (newMode) => {
  if (newMode === 'map' && !map) {
    setTimeout(initializeMap, 100);
    setTimeout(updateMapMarkers, 200);
  } else if (newMode === 'map' && map) {
    setTimeout(() => {
      map?.invalidateSize();
      updateMapMarkers();
    }, 100);
  }
});

onMounted(() => {
  // Set up Leaflet default icon
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  });
});

onUnmounted(() => {
  if (map) {
    map.remove();
    map = null;
  }
});
</script>