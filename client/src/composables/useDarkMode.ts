import { ref, watch } from 'vue';

export function useDarkMode() {
  // Check for saved preference or system preference
  const isDark = ref(
    localStorage.getItem('darkMode') === 'true' ||
    (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches)
  );

  // Watch for changes and update the DOM
  watch(isDark, (newValue) => {
    if (newValue) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', String(newValue));
  }, { immediate: true });

  // Toggle function
  const toggleDarkMode = () => {
    isDark.value = !isDark.value;
  };

  return {
    isDark,
    toggleDarkMode
  };
} 