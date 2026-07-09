import api from "./api";

export const getReport = async (participantId) => {
  const response = await api.get(`/report/${participantId}`);
  return response.data;
};

export const exportReportJSON = async (participantId) => {
  try {
    const response = await api.get(`/report/${participantId}/json`);
    const data = response.data;
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `sherlock_report_${participantId}.json`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    const fallbackData = await getReport(participantId);
    const jsonStr = JSON.stringify(fallbackData, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `sherlock_report_${participantId}.json`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
};
