import api from "./axiosInstance";

export async function getAdminStats() {
  const { data } = await api.get("/admin/stats");
  return data;
}
