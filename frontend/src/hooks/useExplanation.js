import { useEffect, useState } from "react";

import { getParticipantExplanations } from "../services/explanationService";

export default function useExplanation(participantId) {
  const [explanations, setExplanations] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);

  const fetchExplanations = async () => {
    try {
      setLoading(true);

      const data = await getParticipantExplanations(participantId);

      setExplanations(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (participantId) {
      fetchExplanations();
    }
  }, [participantId]);

  return {
    explanations,

    loading,

    error,

    refresh: fetchExplanations,
  };
}
