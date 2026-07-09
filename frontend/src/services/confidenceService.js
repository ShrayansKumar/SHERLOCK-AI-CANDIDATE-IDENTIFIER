import api from "./api";

export const getParticipantConfidence = async (participantId) => {
  const response = await api.get(`/confidence/${participantId}`);

  return response.data;
};

export const getConfidenceTimeline = async (participantId) => {
  const response = await api.get(`/confidence/${participantId}/timeline`);

  return response.data;
};

export const getMeetingConfidence = async (meetingId) => {
  const response = await api.get(`/confidence/meeting/${meetingId}`);

  return response.data;
};
