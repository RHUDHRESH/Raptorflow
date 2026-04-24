declare module "@clerk/nextjs/client" {
  export function getToken(): Promise<string | null>;
}
