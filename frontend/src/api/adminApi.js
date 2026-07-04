import api from "./axiosInstance";

export async function getAdminStats() {
  const { data } = await api.get("/admin/stats");
  return data;
}

export async function listEmployees(params) {
  const { data } = await api.get("/admin/employees", { params });
  return data;
}

