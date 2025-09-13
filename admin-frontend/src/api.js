import axios from "axios";

const BACKEND = process.env.REACT_APP_BACKEND_URL || "http://localhost:5000";
const ADMIN_TOKEN = process.env.REACT_APP_ADMIN_TOKEN || "changeme";

const client = axios.create({
  baseURL: BACKEND,
  headers: { "X-ADMIN-TOKEN": ADMIN_TOKEN }
});

export default client;
