/**
 * Per-browser-session conversation identifier.
 *
 * Generates a UUID once per browser tab session and persists it in
 * `sessionStorage` so a page refresh keeps the same id, but a new tab
 * gets a fresh one. This is NOT persistent memory — `sessionStorage`
 * clears when the tab closes. It only gives the backend a stable
 * conversation handle for the current browser session.
 *
 * Per Issue #3 #8: "per-browser-session conversation identifier ...
 * refresh can reasonably keep the same session ... do not claim this
 * is persistent memory ... no database required."
 */

const STORAGE_KEY = "cs.conversation_id";

function generateId(): string {
  // crypto.randomUUID is available in all modern browsers and secure
  // contexts. Fall back to a RFC4122-v4-ish string for older envs.
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Returns the conversation id for the current browser session.
 * Creates and stores it on first access; reuses on subsequent calls
 * and across page refreshes within the same tab.
 */
export function getConversationId(): string {
  if (typeof window === "undefined") {
    // SSR / build-time: return a stable placeholder. The real id is
    // generated client-side on first use.
    return "ssr-placeholder";
  }
  try {
    let id = sessionStorage.getItem(STORAGE_KEY);
    if (!id) {
      id = generateId();
      sessionStorage.setItem(STORAGE_KEY, id);
    }
    return id;
  } catch {
    // sessionStorage may be unavailable (private mode, disabled). Fall
    // back to an in-memory id for the current page lifecycle.
    return getInMemoryId();
  }
}

let _inMemoryId: string | null = null;
function getInMemoryId(): string {
  if (!_inMemoryId) _inMemoryId = generateId();
  return _inMemoryId;
}
