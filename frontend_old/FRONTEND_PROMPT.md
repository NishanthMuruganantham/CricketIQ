# CricketIQ Frontend — Complete Prompt for Google AI Studio

I need you to generate a complete, production-grade React frontend for CricketIQ — an AI-powered cricket statistics chatbot. The output must be professional-quality code ready for immediate use, not a tutorial demo. Every file must be complete with no placeholders.

---

## 1. Project Context

**CricketIQ** is an AI-powered assistant that answers natural-language questions about Men's T20 International cricket statistics.

- **What it does:** Users type questions like "Who scored the most runs in 2023?" and receive accurate statistical answers with optional visualizations.
- **How it works:** Questions → Django backend → AI generates pandas code → Backend executes query on CSV data → Returns answer + chart data → React displays results.
- **Target quality:** The UI should feel like ChatGPT, Claude.ai, or Perplexity — minimalist, polished, professional. NOT like a tutorial project or hackathon demo.

---

## 2. Complete Architecture

### System Flow

```
User Question
     ↓
React Frontend (POST /api/chat/)
     ↓
Django REST API (/api/chat/)
     ↓
AI Service (Gemini API) generates pandas query
     ↓
Query Engine executes pandas code safely
     ↓
JSON Response { answer, chart_data, query_executed }
     ↓
React renders message + optional chart
```

### Components

1. **Frontend (what you're building):** React 18 + Vite, consumes `/api/chat/` API
2. **Backend (already built):** Django REST API at `http://localhost:8000`
3. **AI Layer:** Gemini generates pandas code, not direct answers
4. **Data Layer:** Two CSVs queried via pandas:
   - `matchwise_data.csv` — match-level summaries
   - `ballwise_data.csv` — ball-by-ball delivery data

---

## 3. API Response Shape (Backend Contract)

The Django backend returns this exact JSON structure:

```json
{
  "answer": "Virat Kohli scored the most runs (741 runs) in 2023.",
  "chart_data": {
    "type": "bar",
    "labels": ["Virat Kohli", "Suryakumar Yadav", "Mohammad Rizwan"],
    "values": [741, 689, 634],
    "title": "Top Run Scorers in 2023",
    "x_axis": "Player",
    "y_axis": "Runs"
  },
  "query_executed": "ball_df.groupby('batter')['batsman_runs'].sum().nlargest(3)"
}
```

**Important notes:**

- `chart_data` can be `null` when no visualization is needed
- `chart_data.type` is one of: `"bar"`, `"line"`, `"pie"`, or `null`
- `query_executed` shows the pandas code that produced the answer (optional to display)

---

## 4. Technology Stack (Exact Requirements)

| Category    | Technology                   | Notes                                  |
| ----------- | ---------------------------- | -------------------------------------- |
| Framework   | React 18                     | Use functional components + hooks only |
| Build Tool  | Vite                         | Latest version                         |
| Styling     | Tailwind CSS v3              | NO other CSS frameworks                |
| Icons       | lucide-react                 | Modern, consistent icon set            |
| Animations  | framer-motion                | Smooth, professional transitions       |
| Charts      | recharts                     | For rendering chart_data               |
| HTTP Client | fetch API                    | Native, no axios required              |
| State       | React hooks + Context API    | No Redux, no Zustand                   |
| Theme       | CSS variables + localStorage | Dark/light mode with system detection  |

**Install dependencies:**

```bash
npm create vite@latest . -- --template react
npm install tailwindcss @tailwindcss/vite lucide-react framer-motion recharts
```

---

## 5. Complete File Structure

Generate every single file in this structure. No files should be skipped.

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js           ← NOT needed if using @tailwindcss/vite
├── src/
│   ├── main.jsx                ← Entry point, renders App
│   ├── App.jsx                 ← Main layout, wraps providers
│   ├── styles/
│   │   └── globals.css         ← Tailwind imports + CSS variables
│   ├── context/
│   │   └── ThemeContext.jsx    ← Dark/light mode provider
│   ├── hooks/
│   │   ├── useChat.js          ← Chat state management
│   │   └── useTheme.js         ← Theme hook (uses context)
│   ├── services/
│   │   └── api.js              ← Backend API calls
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.jsx      ← Logo, theme toggle
│   │   │   └── Container.jsx   ← Max-width wrapper
│   │   ├── chat/
│   │   │   ├── ChatWindow.jsx  ← Message list container
│   │   │   ├── ChatMessage.jsx ← Individual message bubble
│   │   │   ├── ChatInput.jsx   ← Text input + send button
│   │   │   ├── TypingIndicator.jsx ← Loading dots
│   │   │   └── WelcomeScreen.jsx   ← Empty state with suggestions
│   │   ├── charts/
│   │   │   ├── ChartRenderer.jsx ← Switches chart type
│   │   │   ├── BarChart.jsx      ← Bar chart component
│   │   │   └── LineChart.jsx     ← Line chart component
│   │   └── ui/
│   │       ├── ThemeToggle.jsx   ← Animated toggle switch
│   │       └── Button.jsx        ← Reusable button
└── .env.development            ← VITE_API_URL=http://localhost:8000
```

---

## 6. Design Requirements (CRITICAL)

### Quality Reference

Design quality must match these products:

- ✅ ChatGPT — clean, focused, message-driven
- ✅ Claude.ai — elegant threading, professional
- ✅ Perplexity — modern, data-forward
- ✅ Linear — product-grade UI, polished

### NOT Acceptable

- ❌ Generic Bootstrap templates
- ❌ Tutorial-level chat boxes
- ❌ Basic HTML forms with default styling
- ❌ Hackathon MVPs

### Visual Style Mandates

| Aspect     | Requirement                                                                          |
| ---------- | ------------------------------------------------------------------------------------ |
| Colors     | Sophisticated palette — indigo/violet accent, slate grays. NO primary red/blue/green |
| Typography | Inter font family. Minimum 16px on mobile. Clear hierarchy.                          |
| Spacing    | Generous whitespace. Comfortable, not cramped.                                       |
| Borders    | Subtle — use `border-gray-200` (light) or `border-gray-700` (dark)                   |
| Shadows    | Minimal, soft. `shadow-sm` to `shadow-md` maximum                                    |
| Corners    | Rounded — `rounded-xl` for cards, `rounded-2xl` for messages                         |
| Dark Mode  | Default theme. Elegant colors (slate-900 bg, not pure black)                         |
| Animations | Subtle entrance transitions (100-200ms). 60fps. No jank.                             |

### Typography Scale

```css
/* Use Tailwind classes */
.text-xs    → 12px  /* Captions, metadata */
.text-sm    → 14px  /* Secondary text */
.text-base  → 16px  /* Body text, messages */
.text-lg    → 18px  /* Subheadings */
.text-xl    → 20px  /* Section titles */
.text-2xl   → 24px  /* Page titles */
.text-3xl   → 30px  /* Hero text */
```

### Color Palette

```javascript
// tailwind.config.js colors extension
colors: {
  brand: {
    50: '#eef2ff',   // Lightest
    100: '#e0e7ff',
    200: '#c7d2fe',
    300: '#a5b4fc',
    400: '#818cf8',
    500: '#6366f1',  // Primary accent
    600: '#4f46e5',
    700: '#4338ca',
    800: '#3730a3',
    900: '#312e81',  // Darkest
  }
}
```

---

## 7. Component Specifications

### Header.jsx

```
Requirements:
- Sticky at top with backdrop blur effect
- Left: Cricket icon (use BarChart3 from lucide) + "CricketIQ" text
- Right: Theme toggle button
- Brand gradient on icon or text
- Height: ~60px
- Border bottom in light mode, no border in dark mode
- z-index: 50 (above content)
```

**Props:** None (uses ThemeContext internally)

**Styling:**

```
- Background: bg-white/80 dark:bg-slate-900/80 backdrop-blur-md
- Border: border-b border-gray-100 dark:border-gray-800
- Logo text: text-xl font-bold bg-gradient-to-r from-indigo-500 to-purple-500 bg-clip-text text-transparent
```

---

### ChatWindow.jsx

```
Requirements:
- Full height minus header and input (flex-1 overflow-y-auto)
- Auto-scroll to bottom when new messages added (smooth)
- Max-width container (max-w-4xl mx-auto)
- Shows WelcomeScreen when messages.length === 0
- Shows TypingIndicator at bottom when loading === true
- Padding: py-6 px-4
- Space between messages: space-y-6
- Each message gets fade-in animation via Framer Motion
```

**Props:**

- `messages: Array<{ role: 'user' | 'assistant', text: string, chartData?: object, error?: boolean }>`
- `loading: boolean`
- `onSuggestionClick: (question: string) => void` — passed to WelcomeScreen

---

### ChatMessage.jsx

```
Requirements:
- User messages:
  - Right-aligned (justify-end)
  - Gradient background: from-indigo-500 to-purple-600
  - White text
  - User icon avatar (right side)
  - Rounded-2xl corners

- Assistant messages:
  - Left-aligned (justify-start)
  - Card style with subtle shadow
  - Background: bg-gray-50 dark:bg-slate-800
  - Bot icon avatar (left side) with brand color background
  - Rounded-2xl corners

- If message.chartData exists and has type !== null:
  - Render ChartRenderer below the text
  - Wrap chart in a card with padding

- If message.error === true:
  - Add red tint: bg-red-50 dark:bg-red-900/20
  - Text styling: text-red-700 dark:text-red-400

- Entrance animation: { opacity: 0, y: 10 } → { opacity: 1, y: 0 }
- Animation duration: 200ms
```

**Props:**

- `message: { role, text, chartData?, error? }`

---

### ChatInput.jsx

```
Requirements:
- Sticky at bottom of viewport
- Gradient fade above input (from transparent to bg color)
- Textarea that auto-expands (min 1 row, max 5 rows)
- Enter to send, Shift+Enter for new line
- Send button always visible (right side)
- Send button disabled when:
  - Input is empty/whitespace
  - loading === true
- Placeholder: "Ask about cricket stats..."
- Focus ring: ring-2 ring-indigo-500
- Loading state: show spinner inside button, disable input

Dimensions:
- Container: max-w-4xl mx-auto
- Padding: p-4
- Input: rounded-2xl
- Button: w-10 h-10 rounded-full
```

**Props:**

- `onSend: (question: string) => void`
- `disabled: boolean`

---

### WelcomeScreen.jsx

```
Requirements:
- Centered layout (flex items-center justify-center min-h-[60vh])
- Large cricket icon (BarChart3, w-16 h-16, brand color)
- Headline: "Welcome to CricketIQ" (text-3xl font-bold)
- Subheadline: "Ask any question about T20I cricket statistics. Get instant, AI-powered answers." (text-gray-500)
- 4 suggestion cards in a grid:
  - Grid: 2x2 on desktop, 1 column on mobile
  - Each card is a button with icon + text
  - Hover effect: border color change, slight lift
  - onClick: triggers onSuggestionClick(question)

Sample suggestions:
1. TrendingUp icon → "Who scored the most runs in 2023?"
2. Target icon → "Which bowler took the most wickets?"
3. Users icon → "Show me the top 5 run scorers"
4. Award icon → "Who won the most Player of the Match awards?"
```

**Props:**

- `onSuggestionClick: (question: string) => void`

---

### TypingIndicator.jsx

```
Requirements:
- Same layout as assistant message (icon on left)
- Three dots with staggered bounce animation
- Dot size: w-2 h-2
- Dot color: gray-400 dark:gray-500
- Animation: CSS bounce with animation-delay
  - Dot 1: 0ms delay
  - Dot 2: 150ms delay
  - Dot 3: 300ms delay
- Container: same styling as assistant message bubble
```

---

### ThemeToggle.jsx

```
Requirements:
- Toggle switch style (not just button)
- Sun icon for light mode, Moon icon for dark mode
- Smooth slide animation (transform + opacity)
- Width: ~56px
- Height: ~28px
- Circle slides left/right with theme
- Background changes with theme
- Uses Framer Motion for smooth icon transitions
- aria-label="Toggle theme"
```

**Props:**

- `theme: 'dark' | 'light'`
- `onToggle: () => void`

---

### ChartRenderer.jsx

```
Requirements:
- Receives chartData prop
- If chartData is null or chartData.type is null → render nothing
- Switch on chartData.type:
  - "bar" → render BarChart
  - "line" → render LineChart
  - "pie" → render simple message (future implementation)
- Wrapper: rounded-lg bg-gray-50 dark:bg-slate-800 p-4
- Responsive: ResponsiveContainer from recharts
- Height: 300px
```

**Props:**

- `chartData: { type, labels, values, title, x_axis, y_axis }`

---

### BarChart.jsx

```
Requirements:
- Uses recharts BarChart, ResponsiveContainer
- Data transformation: Convert labels + values arrays to:
  [{ name: label[0], value: values[0] }, ...]
- Custom colors matching theme:
  - Bar fill: indigo-500 (#6366f1)
  - Grid: gray-200 dark:gray-700
  - Text: gray-600 dark:gray-300
- Show XAxis with x_axis label
- Show YAxis with y_axis label
- Tooltip on hover
- CartesianGrid with light dashes
- Title displayed above chart
```

**Props:**

- `data: { labels: string[], values: number[], title: string, x_axis: string, y_axis: string }`

---

### LineChart.jsx

```
Requirements:
- Uses recharts LineChart, ResponsiveContainer
- Same data transformation as BarChart
- Line color: indigo-500
- Dot on each point
- Smooth curve (type="monotone")
- Same styling conventions as BarChart
```

---

## 8. Hooks Specifications

### useChat.js

```javascript
/**
 * Custom hook for chat state management.
 *
 * @returns {Object}
 * @property {Array} messages - Array of message objects
 * @property {boolean} loading - True when waiting for API response
 * @property {Function} ask - Function to send a question
 * @property {Function} clearChat - Function to clear all messages
 */
export function useChat() {
  // State
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // Function: ask(question)
  // 1. Validate question is not empty
  // 2. Add user message immediately (optimistic update)
  // 3. Set loading = true
  // 4. Call API: await sendQuestion(question)
  // 5. Add assistant message with response
  // 6. If API error: add error message { role: 'assistant', text: 'Error message', error: true }
  // 7. Set loading = false

  return { messages, loading, ask, clearChat };
}
```

**Message shape:**

```typescript
interface Message {
  role: "user" | "assistant";
  text: string;
  chartData?: {
    type: "bar" | "line" | "pie" | null;
    labels: string[];
    values: number[];
    title: string;
    x_axis: string;
    y_axis: string;
  } | null;
  error?: boolean;
}
```

---

### useTheme.js

```javascript
/**
 * Custom hook for theme management.
 * Uses ThemeContext internally.
 *
 * @returns {Object}
 * @property {string} theme - Current theme: 'dark' | 'light'
 * @property {Function} toggleTheme - Toggle between themes
 * @property {boolean} isDark - Convenience boolean
 */
```

---

## 9. Services Specification

### api.js

```javascript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Send a question to the backend.
 *
 * @param {string} question - User's question
 * @returns {Promise<Object>} - { answer, chart_data, query_executed }
 * @throws {Error} - On network or API error
 */
export async function sendQuestion(question) {
  const response = await fetch(`${API_URL}/api/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
```

---

## 10. Context Specification

### ThemeContext.jsx

```javascript
/**
 * Theme Context Provider
 *
 * Features:
 * 1. Initializes from localStorage if available
 * 2. Falls back to system preference (prefers-color-scheme)
 * 3. Defaults to 'dark' if no preference
 * 4. Persists changes to localStorage
 * 5. Applies 'dark' class to document.documentElement
 *
 * Prevents flash of wrong theme by:
 * - Reading localStorage synchronously in initial state
 * - Script in index.html that sets theme before React loads
 */

export const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    // Check localStorage first
    const saved = localStorage.getItem("cricketiq-theme");
    if (saved) return saved;

    // Check system preference
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }

    // Default to dark
    return "dark";
  });

  useEffect(() => {
    // Apply theme to document
    document.documentElement.classList.toggle("dark", theme === "dark");
    // Persist to localStorage
    localStorage.setItem("cricketiq-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

---

## 11. Tailwind Configuration

### tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["Fira Code", "monospace"],
      },
      colors: {
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
        },
      },
      animation: {
        "fade-in": "fadeIn 0.2s ease-out",
        "slide-up": "slideUp 0.2s ease-out",
        "bounce-slow": "bounce 1s infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
```

---

## 12. Global Styles

### globals.css

```css
@import "tailwindcss";

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.dark ::-webkit-scrollbar-thumb {
  background: #475569;
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Prevent flash of unstyled content */
html.dark {
  color-scheme: dark;
  background-color: #0f172a;
}

html:not(.dark) {
  color-scheme: light;
  background-color: #ffffff;
}

/* Base typography */
body {
  @apply font-sans antialiased;
}

/* Focus styles */
:focus-visible {
  @apply outline-none ring-2 ring-brand-500 ring-offset-2 ring-offset-white dark:ring-offset-slate-900;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Typing indicator dots animation */
@keyframes typing-bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-4px);
  }
}

.typing-dot {
  animation: typing-bounce 1.4s ease-in-out infinite;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.3s;
}
```

---

## 13. Index HTML (Theme Flash Prevention)

### index.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta
      name="description"
      content="CricketIQ - AI-powered T20I cricket statistics assistant"
    />
    <title>CricketIQ</title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code&display=swap"
      rel="stylesheet"
    />

    <!-- Prevent flash of wrong theme -->
    <script>
      (function () {
        const theme = localStorage.getItem("cricketiq-theme");
        if (theme === "light") {
          document.documentElement.classList.remove("dark");
        } else {
          document.documentElement.classList.add("dark");
        }
      })();
    </script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

---

## 14. Accessibility Requirements

All components must meet these accessibility standards:

| Requirement         | Implementation                                                      |
| ------------------- | ------------------------------------------------------------------- |
| Keyboard navigation | Tab through all interactive elements. Enter/Space to activate.      |
| Focus indicators    | Visible focus rings on all interactive elements                     |
| ARIA labels         | All buttons have descriptive aria-label attributes                  |
| Screen reader       | New messages announced. Use aria-live="polite" on message container |
| Color contrast      | Meet WCAG AA (4.5:1 for text, 3:1 for UI elements)                  |
| Reduced motion      | Respect prefers-reduced-motion media query                          |
| Form labels         | All inputs have associated labels (can be visually hidden)          |

**Specific ARIA requirements:**

- Send button: `aria-label="Send message"`
- Theme toggle: `aria-label="Toggle theme"`
- Message container: `aria-live="polite" aria-label="Chat messages"`
- Each suggestion card: Clear, descriptive text

---

## 15. Performance Requirements

| Requirement         | Implementation                     |
| ------------------- | ---------------------------------- |
| Lazy load charts    | Use React.lazy() for ChartRenderer |
| Memoize messages    | Use React.memo() for ChatMessage   |
| No layout shifts    | Reserve space for loading states   |
| Fast initial render | < 100ms to interactive             |
| Smooth animations   | 60fps, use transform/opacity only  |
| Bundle size         | Keep < 200KB gzipped               |

---

## 16. Responsive Breakpoints

Design mobile-first. Test at these widths:

| Breakpoint | Width          | Behavior                                  |
| ---------- | -------------- | ----------------------------------------- |
| Mobile     | 320px - 767px  | Single column, compact spacing            |
| Tablet     | 768px - 1023px | Comfortable spacing                       |
| Desktop    | 1024px+        | Max-width containers, generous whitespace |

**Mobile-specific requirements:**

- Message bubbles: max-w-[90%]
- Font size: minimum 16px to prevent zoom
- Touch targets: minimum 44x44px
- Keyboard: Input should not be covered when keyboard opens

---

## 17. Code Quality Standards

Every file must follow these standards:

1. **Imports organized:** React, external libs, local imports (with blank lines between)
2. **PropTypes or JSDoc:** Document all props with types
3. **No magic numbers:** Extract to named constants
4. **Consistent naming:**
   - Components: PascalCase
   - Hooks: camelCase with `use` prefix
   - Constants: UPPER_SNAKE_CASE
   - Files: Match export name
5. **No inline styles:** Tailwind classes only
6. **Comments for complex logic:** Explain the "why" not the "what"
7. **Error boundaries:** Wrap Chart components in error boundary
8. **Loading states:** Every async operation shows loading feedback

---

## 18. Quality Checklist

The generated code must pass ALL of these checks:

- [ ] `npm install` completes without errors
- [ ] `npm run dev` starts without console errors
- [ ] No ESLint warnings or errors
- [ ] Dark mode works with no flash of light theme on load
- [ ] Theme preference persists across page reload
- [ ] Mobile responsive (tested at 320px width)
- [ ] Animations are smooth (60fps)
- [ ] Auto-scroll works when new messages arrive
- [ ] Send button correctly disabled when input empty
- [ ] Send button correctly disabled while loading
- [ ] Enter sends message, Shift+Enter adds newline
- [ ] Typing indicator appears during API calls
- [ ] Error messages display gracefully
- [ ] Suggestion cards on welcome screen trigger chat
- [ ] Charts render correctly from chartData
- [ ] All buttons have aria-labels
- [ ] Focus indicators are visible
- [ ] No console warnings or errors

---

## 19. Output Format Requirements

Generate these exact files with COMPLETE code:

1. `package.json` — All dependencies listed
2. `vite.config.js` — Vite + Tailwind configuration
3. `tailwind.config.js` — Full config with customizations
4. `index.html` — With theme flash prevention script
5. `src/main.jsx` — Entry point
6. `src/App.jsx` — Main layout
7. `src/styles/globals.css` — All global styles
8. `src/context/ThemeContext.jsx` — Complete provider
9. `src/hooks/useChat.js` — Complete implementation
10. `src/hooks/useTheme.js` — Complete implementation
11. `src/services/api.js` — Complete API service
12. `src/components/layout/Header.jsx` — Complete component
13. `src/components/layout/Container.jsx` — Complete component
14. `src/components/chat/ChatWindow.jsx` — Complete component
15. `src/components/chat/ChatMessage.jsx` — Complete component
16. `src/components/chat/ChatInput.jsx` — Complete component
17. `src/components/chat/TypingIndicator.jsx` — Complete component
18. `src/components/chat/WelcomeScreen.jsx` — Complete component
19. `src/components/charts/ChartRenderer.jsx` — Complete component
20. `src/components/charts/BarChart.jsx` — Complete component
21. `src/components/charts/LineChart.jsx` — Complete component
22. `src/components/ui/ThemeToggle.jsx` — Complete component
23. `src/components/ui/Button.jsx` — Complete component
24. `.env.development` — Environment variables

**For each file:**

- Include ALL imports at the top
- Include complete, working code (no "// rest of implementation...")
- Include brief comments explaining non-obvious logic
- Include proper exports
- Make sure the code compiles and runs

---

## 20. Setup Instructions

After generating, these commands should work:

```bash
cd frontend
npm install
npm run dev
```

The app should:

1. Start on http://localhost:5173
2. Display the dark-themed welcome screen
3. Allow theme toggle to light mode
4. Show sample question cards
5. Allow sending questions (will error without backend, but should show error gracefully)

---

Generate all files with complete code. No placeholders. Ready for immediate use.
