import api from "./axiosInstance";

export async function getMyProfile() {
  const { data } = await api.get("/profile/me");
  return data;
}

export async function updateMyProfile(payload) {
  const { data } = await api.patch("/profile/me", payload);
  return data;
}

export async function getUserProfile(userId) {
  const { data } = await api.get(`/profile/${userId}`);
  return data;
}

export async function updateUserProfile(userId, payload) {
  const { data } = await api.patch(`/profile/${userId}`, payload);
  return data;
}
