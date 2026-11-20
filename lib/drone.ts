import axios from "axios";

// Relative by default: in development Next.js rewrites /api/* to the Flask
// server (see next.config.js). Override with NEXT_PUBLIC_API_BASE if needed.
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE ?? "/api";

const api = axios.create({ baseURL: API_BASE_URL, timeout: 15000 });

export interface DroneInfo {
  name: string;
  description: string;
  capabilities: string[];
  max_speed: number | null;
  max_altitude: number | null;
  simulated: boolean;
}

export interface DroneStatus {
  status: string;
  flight_time: number | null;
  battery_level: number | null;
  speed: number | null;
  distance: number | null;
  temperature: number | null;
  altitude: number | null;
  is_flying: boolean;
  sequence_running: boolean;
  x: number | null;
  y: number | null;
  heading: number | null;
}

/** Message from the API (`{ message }`) when available, else a fallback. */
export const errorMessage = (error: unknown, fallback: string): string => {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.message ?? fallback;
  }
  return fallback;
};

export const getDroneInfo = async (): Promise<DroneInfo> =>
  (await api.get("/drone_info")).data;

export const getStatus = async (): Promise<DroneStatus> =>
  (await api.get("/drone_status")).data;

export const takeoff = async () => (await api.post("/takeoff")).data;
export const land = async () => (await api.post("/land")).data;
export const emergencyStop = async () =>
  (await api.post("/emergency_stop")).data;

/** Legacy single-direction command (forward, backward, left, right, up, down, cw, ccw). */
export const control = async (direction: string, speed = 50) =>
  (await api.post("/control", { direction, speed })).data;

export const performSequence = async () =>
  (await api.post("/perform_sequence")).data;
export const abortSequence = async () =>
  (await api.post("/abort_sequence")).data;

export const getVideoFeedUrl = () => `${API_BASE_URL}/video_feed`;
