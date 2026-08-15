import { handleAuth } from "@auth0/nextjs-auth0";

// Auth0 v3 is the stable SDK line compatible with the current Next 14 app.
export const GET = handleAuth();
