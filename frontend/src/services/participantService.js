import api from "./api";

export const getParticipants = async () => {
  try {
    const response = await api.get("/participants");

    return response.data;
  } catch (error) {
    console.error("Failed to fetch participants:", error);
    throw error;
  }
};
