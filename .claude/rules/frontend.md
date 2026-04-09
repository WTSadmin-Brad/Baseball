---
paths:
  - "frontend/src/**"
---

# Frontend Patterns

## Component Structure

Components live in `frontend/src/components/`. Each is a single `.jsx` file with inline styles (no CSS modules or Tailwind — keeping it simple).

## State Management

- `useSession.js` hook manages all API communication and session state
- No Redux/Zustand — single hook provides session, frames, active frame, loading state
- Canvas-local state (dragging markers, dirty flags) stays in `FrameViewer.jsx`

## Styling

- Dark theme with CSS variables defined in `index.css` (--bg, --surface, --border, --accent, etc.)
- Inline styles on components (not CSS classes) — keeps components self-contained
- Color variables for swing analysis palette: --hip-color, --shoulder-color, --front-arm, etc.

## Canvas Rendering

- `FrameViewer.jsx` handles the Canvas overlay for "Markers" mode
- Image is rendered as an `<img>` tag; Canvas sits on top as an absolute-positioned overlay
- Landmarks stored as normalized [0,1] coordinates; converted to pixel coords at render time using image display dimensions
- Skeleton connections come from `/api/config` endpoint (backend is source of truth for connection topology)
- Marker hit detection: find closest landmark within a radius on mousedown, then track mousemove for drag

## API Pattern

All API calls go through `useSession.js`:
```js
const api = (path, opts) => fetch(`/api${path}`, opts).then(r => r.json());
```
- Backend at `/api/*`, proxied during dev via Vite config
- File uploads use `FormData`
- Landmark updates use `PUT` with JSON body
