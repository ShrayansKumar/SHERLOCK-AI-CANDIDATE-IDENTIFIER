import api from "./api";

export const uploadAudio = async (participantId, meetingId, file, onProgress) => {
  const formData = new FormData();
  formData.append("participant_id", participantId);
  formData.append("meeting_id", meetingId);
  formData.append("audio_file", file);
  const response = await api.post("/audio/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: onProgress
      ? (e) => {
          if (e.total) {
            onProgress(Math.round((e.loaded * 100) / e.total));
          }
        }
      : undefined,
  });
  return response.data;
};

export const getParticipantAudio = async (participantId) => {
  const response = await api.get(`/audio/${participantId}`);
  return response.data;
};

export const getMeetingAudio = async (meetingId) => {
  const response = await api.get(`/audio/meeting/${meetingId}`);
  return response.data;
};
