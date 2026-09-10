import axios from "axios";

const baseURL = `${import.meta.env.BASE_URL.replace(/\/$/, "")}/api`;

const apiClient = axios.create({
  baseURL,
  withCredentials: true,
  xsrfCookieName: "__PKG___csrftoken",
  xsrfHeaderName: "X-CSRFToken",
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;
