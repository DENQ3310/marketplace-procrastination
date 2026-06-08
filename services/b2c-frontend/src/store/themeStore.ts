import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'light' | 'dark';

interface ThemeStore {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      theme: 'light',
      
      toggleTheme: () => set((state) => {
        const newTheme: Theme = state.theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        return { theme: newTheme };
      }),
      
      setTheme: (theme: Theme) => set(() => {
        document.documentElement.setAttribute('data-theme', theme);
        return { theme };
      }),
    }),
    {
      name: 'theme-storage',
      onRehydrateStorage: () => (state) => {
        if (state) {
          document.documentElement.setAttribute('data-theme', state.theme);
        }
      },
    }
  )
);

export default useThemeStore;
