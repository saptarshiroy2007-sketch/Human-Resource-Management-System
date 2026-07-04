import api from "./axiosInstance";

export async function login(email, password) {
  const formData = new URLSearchParams();
  formData.set("username", email);
  formData.set("password", password);

  const { data } = await api.post("/auth/login", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  return data;
}

export async function getMe() {
  const { data } = await api.get("/auth/me");
  return data;
}

export async function refresh(refreshToken) {
  const { data } = await api.post("/auth/refresh", null, {
    params: { refresh_token: refreshToken },
  });

  return data;
}

export async function logout() {
  await api.post("/auth/logout");
}
