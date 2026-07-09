import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "../pages/Dashboard";
import AudioUploadPage from "../pages/AudioUploadPage";
import VideoUploadPage from "../pages/VideoUploadPage";
import ReportPage from "../pages/ReportPage";
import ParticipantsPage from "../pages/ParticipantsPage";
import ReasoningPage from "../pages/ReasoningPage";
import ConfidencePage from "../pages/ConfidencePage";
import EvidencePage from "../pages/EvidencePage";
import NewInterviewPage from "../pages/NewInterviewPage";
import LiveInterviewPage from "../pages/LiveInterviewPage";
import HistoryPage from "../pages/HistoryPage";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Session-based workflow */}
        <Route path="/new-interview"      element={<NewInterviewPage />} />
        <Route path="/live/:meetingDbId"  element={<LiveInterviewPage />} />
        <Route path="/history"            element={<HistoryPage />} />

        {/* Analysis pages */}
        <Route path="/participants"       element={<ParticipantsPage />} />
        <Route path="/confidence"         element={<ConfidencePage />} />
        <Route path="/reasoning"          element={<ReasoningPage />} />
        <Route path="/evidence"           element={<EvidencePage />} />
        <Route path="/report"             element={<ReportPage />} />

        {/* Offline upload (kept for dev/testing) */}
        <Route path="/audio"              element={<AudioUploadPage />} />
        <Route path="/video"              element={<VideoUploadPage />} />

        {/* Dashboard (home) */}
        <Route path="/"                   element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;