import { useEffect, useState } from "react";
import { getMeetings } from "../services/meetingService";

function useMeetings() {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        const data = await getMeetings();
        setMeetings(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchMeetings();
  }, []);

  return {
    meetings,
    loading,
    error,
  };
}

export default useMeetings;
