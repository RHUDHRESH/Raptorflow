import { redirect } from "next/navigation";

export default function AppPageRedirect() {
  redirect("/app/dashboard");
}
