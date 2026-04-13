export async function register(): Promise<void> {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    console.log("instrumentation scaffold registered");
  }
}
