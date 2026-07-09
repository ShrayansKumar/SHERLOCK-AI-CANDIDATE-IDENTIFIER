import axios from "axios";

const host = typeof window !== "undefined" && window.location.hostname ? window.location.hostname : "localhost";

const api = axios.create({
  baseURL: `http://${host}:8000/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
