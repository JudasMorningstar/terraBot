import { create } from "zustand";
import axios from "axios";
import { DroneState } from "@/types";
import { toast } from "sonner";
import { get } from "http";

const API_BASE_URL = "http://localhost:3000/api";
const useDroneStore = create<DroneState>((set, get) => ({
  isFlying: false,
  flight_time: null,
  batteryLevel: null,
  speed: null,
  distance: null,
  temperature: null,
  altitude: null,
  videoFeedUrl: `${API_BASE_URL}/video_feed`,
  warningMessage: "",
  takeoff: async () => {
    try {
      const { batteryLevel } = get();
      if (batteryLevel !== null && batteryLevel < 10) {
        set({ warningMessage: "Battery level is too low to take off." });
        toast.warning("Battery level is too low to take off.");
        return;
      }
      await axios.post(`${API_BASE_URL}/takeoff`);
      set({ isFlying: true, warningMessage: "" });
    } catch (error) {
      console.error(error);
      toast.error("Error taking off.");
    }
  },
  land: async () => {
    try {
      await axios.post(`${API_BASE_URL}/land`);
      set({ isFlying: false });
    } catch (error) {
      console.error("Error landing:", error);
    }
  },
  fetchDroneStatus: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/drone_status`);
      const data = response.data;
      if (data.status === "success") {
        set({
          flight_time: data.flight_time,
          batteryLevel: data.battery_level,
          speed: data.speed,
          distance: data.distance,
          temperature: data.temperature,
          altitude: data.altitude,
        });
      } else {
        console.error("Error fetching drone status:", data.message);
        // toast.error(data.message);
      }
    } catch (error) {
      console.error("Error fetching drone status:", error);
    }
  },
}));

export default useDroneStore;
