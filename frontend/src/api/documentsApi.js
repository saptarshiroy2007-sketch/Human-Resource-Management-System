import api from "./axiosInstance";

export async function uploadDocument(docType, file) {
  const formData = new FormData();
  formData.set("doc_type", docType);
  formData.set("file", file);

  const { data } = await api.post("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getMyDocuments() {
  const { data } = await api.get("/documents/me");
  return data;
}

export async function deleteDocument(documentId) {
  await api.delete(`/documents/${documentId}`);
}
