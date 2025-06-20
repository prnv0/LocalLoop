<template>
  <div class="flex flex-col h-full bg-white dark:bg-gray-800">
    <!-- Header with View Toggle -->
    <div class="flex-shrink-0 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          {{ currentItinerary?.summary || 'Your Itinerary' }}
        </h2>
        <div class="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
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
      <div v-if="!currentItinerary || !currentItinerary.ordered_places || currentItinerary.ordered_places.length === 0" 
           class="flex items-center justify-center h-full text-center p-8">
        <div class="max-w-sm">
          <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">No Itinerary Yet</h3>
          <p class="text-gray-500 dark:text-gray-400">Start chatting to create your travel itinerary!</p>
        </div>
      </div>

      <!-- List View -->
      <div v-else-if="viewMode === 'list'" class="h-full overflow-y-auto custom-scrollbar">
        <div class="p-4 space-y-4">
          <div
            v-for="(place, index) in currentItinerary.ordered_places"
            :key="place.id"
            class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors animate-fade-in"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-2 mb-2">
                  <span class="inline-flex items-center justify-center w-6 h-6 bg-primary-500 text-white text-sm font-medium rounded-full">
                    {{ index + 1 }}
                  </span>
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white">{{ place.name }}</h3>
                  <div v-if="place.rating" class="flex items-center">
                    <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                    <span class="ml-1 text-sm text-gray-600 dark:text-gray-300">{{ place.rating }}</span>
                  </div>
                </div>
                <p class="text-gray-600 dark:text-gray-300 text-sm mb-2">{{ place.address }}</p>
                <div v-if="currentItinerary.legs[index]" class="text-sm text-gray-500 dark:text-gray-400">
                  🚗 {{ currentItinerary.legs[index].duration }} ({{ currentItinerary.legs[index].distance }})
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <button
                  @click="editStop(place)"
                  class="text-gray-400 hover:text-primary-500 transition-colors"
                  title="Edit stop"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                </button>
                <button
                  @click="removeStop(place)"
                  class="text-gray-400 hover:text-red-500 transition-colors"
                  title="Remove stop"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Add Stop Button (moved to bottom) -->
          <button
            @click="showAddStopForm = true"
            class="w-full flex items-center justify-center space-x-2 bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-4 py-3 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            <span>Add Stop</span>
          </button>
        </div>

        <!-- Add Stop Modal -->
        <div v-if="showAddStopForm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Add New Stop</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Location Name</label>
                <input
                  v-model="locationName"
                  type="text"
                  placeholder="Enter location name (e.g., Central Park, Empire State Building)"
                  class="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Place Type (Optional)</label>
                <select
                  v-model="selectedPlaceType"
                  class="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700"
                >
                  <option value="">Select a type (optional)</option>
                  <option value="restaurant">Restaurant</option>
                  <option value="cafe">Cafe</option>
                  <option value="museum">Museum</option>
                  <option value="park">Park</option>
                  <option value="shopping">Shopping</option>
                  <option value="attraction">Attraction</option>
                </select>
              </div>
              <div class="flex justify-end space-x-3">
                <button
                  @click="closeAddForm"
                  class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button
                  @click="addStop"
                  :disabled="!locationName"
                  class="px-4 py-2 text-sm font-medium text-white bg-primary-500 hover:bg-primary-600 rounded-md transition-colors disabled:opacity-50"
                >
                  Add Stop
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Edit Stop Modal -->
        <div v-if="showEditStopForm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Edit Stop</h3>
            <form @submit.prevent="submitEditStop" class="space-y-4">
              <div>
                <label for="edit-location" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Location Name</label>
                <input
                  id="edit-location"
                  v-model="locationName"
                  type="text"
                  required
                  placeholder="Enter new location name"
                  class="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                />
              </div>
              <div>
                <label for="edit-type" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Place Type (Optional)</label>
                <select
                  id="edit-type"
                  v-model="selectedPlaceType"
                  class="w-full text-sm border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700"
                >
                  <option value="">Select a type (optional)</option>
                  <option value="restaurant">Restaurant</option>
                  <option value="cafe">Cafe</option>
                  <option value="museum">Museum</option>
                  <option value="park">Park</option>
                  <option value="shopping">Shopping</option>
                  <option value="attraction">Attraction</option>
                </select>
              </div>
              <div class="flex justify-end space-x-3">
                <button
                  type="button"
                  @click="closeEditForm"
                  class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="!locationName"
                  class="px-4 py-2 text-sm font-medium text-white bg-primary-500 hover:bg-primary-600 rounded-md transition-colors disabled:opacity-50"
                >
                  Save Changes
                </button>
              </div>
            </form>
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
    <div v-if="currentItinerary && currentItinerary.ordered_places.length > 0" 
         class="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 px-4 py-3 bg-gray-50 dark:bg-gray-700">
      <div class="flex items-center justify-between text-sm">
        <span class="text-gray-600 dark:text-gray-300">
          {{ currentItinerary.ordered_places.length }} stop{{ currentItinerary.ordered_places.length > 1 ? 's' : '' }}
        </span>
        <span v-if="currentItinerary.legs.length > 0" class="text-gray-600 dark:text-gray-300">
          Total: {{ currentItinerary.legs.reduce((total, leg) => {
            const minutes = parseInt(leg.duration.split(' ')[0]);
            return total + (isNaN(minutes) ? 0 : minutes);
          }, 0) }} mins
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import L from 'leaflet';
import type { Itinerary, ViewMode, Place } from '../types';

interface Props {
  currentItinerary: Itinerary | null;
}

interface Emits {
  (e: 'remove-stop', stopId: string): void;
  (e: 'edit-stop', stopId: string, locationName: string, placeType?: string): void;
  (e: 'add-stop', locationName: string, placeType?: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const viewMode = ref<ViewMode>('list');
const mapContainer = ref<HTMLElement>();
let map: L.Map | null = null;
let markers: L.Marker[] = [];

// Form state
const showAddStopForm = ref(false);
const showEditStopForm = ref(false);
const selectedPlaceType = ref<string>('');
const locationName = ref<string>('');
const editingStopId = ref<string>('');

const closeAddForm = () => {
  showAddStopForm.value = false;
  locationName.value = '';
  selectedPlaceType.value = '';
};

const closeEditForm = () => {
  showEditStopForm.value = false;
  locationName.value = '';
  selectedPlaceType.value = '';
  editingStopId.value = '';
};

const removeStop = (place: Place) => {
  const stopId = (place.id as string | undefined) || (place as any).place_id || '';
  if (stopId) {
    emit('remove-stop', stopId);
  }
};

const editStop = (place: Place) => {
  editingStopId.value = place.id;
  locationName.value = place.name;
  selectedPlaceType.value = ''; // Reset type selection
  showEditStopForm.value = true;
};

const submitEditStop = () => {
  if (locationName.value && editingStopId.value) {
    emit('edit-stop', editingStopId.value, locationName.value, selectedPlaceType.value);
    closeEditForm();
  }
};

const addStop = () => {
  if (locationName.value) {
    emit('add-stop', locationName.value, selectedPlaceType.value);
    closeAddForm();
  }
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
  if (!map || !props.currentItinerary || !props.currentItinerary.ordered_places) return;

  // Clear existing markers
  markers.forEach(marker => map?.removeLayer(marker));
  markers = [];

  const places = props.currentItinerary.ordered_places;
  if (places.length === 0) return;

  // Add markers for each stop (support lat/lng or latitude/longitude keys)
  places.forEach((place, index) => {
    const lat = (place as any).lat !== undefined ? (place as any).lat : (place as any).latitude;
    const lng = (place as any).lng !== undefined ? (place as any).lng : (place as any).longitude;
    if (lat === undefined || lng === undefined) return;
    const marker = L.marker([lat, lng])
      .addTo(map!)
      .bindPopup(`
        <div class="p-2">
          <h3 class="font-medium">${index + 1}. ${place.name}</h3>
          <p class="text-sm text-gray-600">${place.address}</p>
          ${place.rating ? `<p class="text-sm">⭐ ${place.rating}</p>` : ''}
        </div>
      `);
    markers.push(marker);
  });

  // Draw polyline connecting stops
  if (places.length > 1) {
    const coordinates = places.map(place => {
      const lat = (place as any).lat !== undefined ? (place as any).lat : (place as any).latitude;
      const lng = (place as any).lng !== undefined ? (place as any).lng : (place as any).longitude;
      return [lat, lng] as [number, number];
    });
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