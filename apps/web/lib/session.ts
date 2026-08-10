/**
 * Per-browser-session prototype scope identifiers.
 *
 * Generates separate random user and conversation ids once per browser
 * tab session and persists them in `sessionStorage`, so a page refresh
 * keeps the same prototype scope but a new tab gets a fresh one. The
 * user id is NOT authentication and neither id is durable identity.
 *
 * Per Issue #3 #8: "per-browser-session conversation identifier ...
 * refresh can reasonably keep the same session ... do not claim this
 * is persistent memory ... no database required."
 */

const CONVERSATION_STORAGE_KEY = "rq.conversation_id";
const USER_STORAGE_KEY = "rq.prototype_user_id";
const LEGACY_CONVERSATION_STORAGE_KEY = "cs.conversation_id";
const CLIENT_SCOPE_ID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function isClientScopeId(value: string): boolean {
  return CLIENT_SCOPE_ID_PATTERN.test(value);
}

function generateId(): string {
  // randomUUID requires a secure context in browsers. getRandomValues is
  // the secure fallback for deployments where that convenience API is not
  // exposed. Prototype scopes fail closed if Web Crypto is unavailable.
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  if (typeof crypto !== "undefined" && typeof crypto.getRandomValues === "function") {
    const bytes = crypto.getRandomValues(new Uint8Array(16));
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  }
  throw new Error("Secure random identifiers are unavailable.");
}

/**
 * Returns the conversation id for the current browser session.
 * Creates and stores it on first access; reuses on subsequent calls
 * and across page refreshes within the same tab.
 */
function getSessionId(
  storageKey: string,
  ssrPlaceholder: string,
  memoryKey: "conversation" | "user",
  legacyStorageKey?: string,
): string {
  if (typeof window === "undefined") {
    return ssrPlaceholder;
  }
  try {
    let id = sessionStorage.getItem(storageKey);
    if (id && !isClientScopeId(id)) {
      sessionStorage.removeItem(storageKey);
      id = null;
    }
    if (!id && legacyStorageKey) {
      id = sessionStorage.getItem(legacyStorageKey);
      if (id && isClientScopeId(id)) {
        sessionStorage.setItem(storageKey, id);
        sessionStorage.removeItem(legacyStorageKey);
      } else if (id) {
        sessionStorage.removeItem(legacyStorageKey);
        id = null;
      }
    }
    if (!id) {
      id = generateId();
      sessionStorage.setItem(storageKey, id);
    }
    return id;
  } catch {
    return getInMemoryId(memoryKey);
  }
}

const inMemoryIds: { conversation: string | null; user: string | null } = {
  conversation: null,
  user: null,
};

function getInMemoryId(key: "conversation" | "user"): string {
  const existing = inMemoryIds[key];
  if (existing) return existing;
  const generated = generateId();
  inMemoryIds[key] = generated;
  return generated;
}

/** Stable conversation handle for this browser tab session. */
export function getConversationId(): string {
  return getSessionId(
    CONVERSATION_STORAGE_KEY,
    "ssr-conversation",
    "conversation",
    LEGACY_CONVERSATION_STORAGE_KEY,
  );
}

/**
 * Random prototype scope for this browser tab session.
 * This value is caller-controlled and MUST NOT be treated as authentication.
 */
export function getPrototypeUserId(): string {
  return getSessionId(USER_STORAGE_KEY, "ssr-prototype-user", "user");
}
