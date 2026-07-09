import { useEffect, useState, useCallback } from "react";
import { getParticipantTranscripts } from "../services/transcriptService";

export default function useTranscript(participantId) {
  const [transcripts, setTranscripts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTranscripts = useCallback(async () => {
    if (!participantId) return;
    try {
      setLoading(true);
      const data = await getParticipantTranscripts(participantId);
      setTranscripts(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [participantId]);

  useEffect(() => {
    fetchTranscripts();
  }, [fetchTranscripts]);

  return { transcripts, loading, error, refresh: fetchTranscripts };
}
