import api from "./axiosInstance";

function withDateRange(params = {}) {
  return {
    params: {
      start_date: params.startDate || undefined,
      end_date: params.endDate || undefined,
    },
  };
}

export async function checkIn() {
  const { data } = await api.post("/attendance/check-in");
  return data;
}

export async function checkOut() {
  const { data } = await api.post("/attendance/check-out");
  return data;
}

export async function getMyAttendance(params) {
  const { data } = await api.get("/attendance/me", withDateRange(params));
  return data;
}

export async function getAllAttendance(params) {
  const { data } = await api.get("/attendance/all", withDateRange(params));
  return data;
}

export async function getUserAttendance(userId, params) {
  const { data } = await api.get(`/attendance/${userId}`, withDateRange(params));
  return data;
}
