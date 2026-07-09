import api from "./api";

export const getParticipantExplanations = async (participantId) => {
  const response = await api.get(`/explanations/${participantId}`);

  return response.data;
};

export const getMeetingExplanations = async (meetingId) => {
  const response = await api.get(`/explanations/meeting/${meetingId}`);

  return response.data;
};
