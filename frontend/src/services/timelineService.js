import api from "./api";

export const getConfidenceTimeline = async (participantId) => {
  const response = await api.get(`/confidence/${participantId}/timeline`);

  return response.data;
};
