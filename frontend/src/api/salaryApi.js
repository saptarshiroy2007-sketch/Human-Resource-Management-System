import api from "./axiosInstance";

export async function getMySalaryHistory() {
  const { data } = await api.get("/salary/me");
  return data;
}

export async function getMyCurrentSalary() {
  const { data } = await api.get("/salary/me/current");
  return data;
}

export async function getUserSalaryHistory(userId) {
  const { data } = await api.get(`/salary/${userId}`);
  return data;
}

export async function updateUserSalary(userId, payload) {
  const { data } = await api.post(`/salary/${userId}/update`, payload);
  return data;
}
