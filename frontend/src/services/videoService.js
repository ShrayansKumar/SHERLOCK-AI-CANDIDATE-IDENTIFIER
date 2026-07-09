import api from "./api";

export const uploadVideo = async (participantId, meetingId, file, onProgress) => {
  const formData = new FormData();
  formData.append("participant_id", participantId);
  formData.append("meeting_id", meetingId);
  formData.append("video_file", file);
  const response = await api.post("/video/upload", formData, {
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

export const getParticipantVideo = async (participantId) => {
  const response = await api.get(`/video/${participantId}`);
  return response.data;
};

export const getMeetingVideo = async (meetingId) => {
  const response = await api.get(`/video/meeting/${meetingId}`);
  return response.data;
};
