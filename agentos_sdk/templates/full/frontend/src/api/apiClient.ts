import axios from "axios";

const baseURL = "/api";

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
