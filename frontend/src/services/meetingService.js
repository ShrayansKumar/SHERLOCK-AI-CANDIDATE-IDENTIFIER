import api from "./api";

export const getMeetings = async () => {
  const response = await api.get("/meetings");
  return response.data;
};

export const getMeetingHistory = async () => {
  const response = await api.get("/meetings/history");
  return response.data;
};

export const createMeeting = async (data) => {
  const response = await api.post("/meetings", data);
  return response.data;
};

export const startInterview = async (meetingDbId) => {
  const response = await api.post(`/meetings/${meetingDbId}/start`);
  return response.data;
};

export const endInterview = async (meetingDbId) => {
  const response = await api.post(`/meetings/${meetingDbId}/end`);
  return response.data;
};

export const deleteMeeting = async (meetingDbId) => {
  const response = await api.delete(`/meetings/${meetingDbId}`);
  return response.data;
};
