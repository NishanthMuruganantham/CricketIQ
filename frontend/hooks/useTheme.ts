import { useThemeContext } from '../context/ThemeContext.tsx';

export const useTheme = () => {
  return useThemeContext();
};