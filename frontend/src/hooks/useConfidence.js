import { useEffect, useState } from "react";

import { getMeetingConfidence } from "../services/confidenceService";

export default function useConfidence(meetingId) {
  const [confidence, setConfidence] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);

  const fetchConfidence = async () => {
    try {
      setLoading(true);

      const data = await getMeetingConfidence(meetingId);

      setConfidence(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (meetingId) {
      fetchConfidence();
    }
  }, [meetingId]);

  return {
    confidence,

    loading,

    error,

    refresh: fetchConfidence,
  };
}
