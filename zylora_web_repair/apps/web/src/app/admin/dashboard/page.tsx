import { redirect } from "next/navigation";

export default function AdminDashboardRedirect() {
  redirect("/admin/sites/demo-business/dashboard");
}
