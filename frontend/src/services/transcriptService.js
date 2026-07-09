import api from "./api";

export const getParticipantTranscripts = async (participantId) => {
  const response = await api.get(`/transcripts/${participantId}`);
  return response.data;
};

export const getMeetingTranscripts = async (meetingId) => {
  const response = await api.get(`/transcripts/meeting/${meetingId}`);
  return response.data;
};
