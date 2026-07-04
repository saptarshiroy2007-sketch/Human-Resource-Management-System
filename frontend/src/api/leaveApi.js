import api from "./axiosInstance";

export async function applyLeave(payload) {
  const { data } = await api.post("/leave/apply", payload);
  return data;
}

export async function getMyLeaves(leaveStatus) {
  const { data } = await api.get("/leave/me", {
    params: { leave_status: leaveStatus || undefined },
  });
  return data;
}

export async function cancelLeave(leaveId) {
  await api.post(`/leave/${leaveId}/cancel`);
}

export async function getAllLeaves(leaveStatus) {
  const { data } = await api.get("/leave/all", {
    params: { leave_status: leaveStatus || undefined },
  });
  return data;
}

export async function approveLeave(leaveId, adminComment) {
  const { data } = await api.post(`/leave/${leaveId}/approve`, {
    admin_comment: adminComment || null,
  });
  return data;
}

export async function rejectLeave(leaveId, adminComment) {
  const { data } = await api.post(`/leave/${leaveId}/reject`, {
    admin_comment: adminComment || null,
  });
  return data;
}
