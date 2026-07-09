import { useEffect, useState } from "react";
import { getParticipants } from "../services/participantService";

function useParticipants() {
  const [participants, setParticipants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchParticipants = async () => {
      try {
        const data = await getParticipants();
        setParticipants(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchParticipants();
  }, []);

  return {
    participants,
    loading,
    error,
  };
}

export default useParticipants;
