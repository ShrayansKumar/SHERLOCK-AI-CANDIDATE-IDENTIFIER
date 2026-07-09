import { useEffect, useState } from "react";

import { getConfidenceTimeline } from "../services/timelineService";

export default function useTimeline(participantId) {
  const [timeline, setTimeline] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);

  const fetchTimeline = async () => {
    try {
      setLoading(true);

      const data = await getConfidenceTimeline(participantId);

      setTimeline(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (participantId) {
      fetchTimeline();
    }
  }, [participantId]);

  return {
    timeline,

    loading,

    error,

    refresh: fetchTimeline,
  };
}
