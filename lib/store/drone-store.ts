import { create } from "zustand";
import { toast } from "sonner";
import * as droneApi from "@/lib/drone";
import type { DroneInfo } from "@/lib/drone";

interface DroneState {
  // Connection
  connected: boolean;
  info: DroneInfo | null;
  // Telemetry
  isFlying: boolean;
  sequenceRunning: boolean;
  flight_time: number | null;
  batteryLevel: number | null;
  speed: number | null;
  distance: number | null;
  temperature: number | null;
  altitude: number | null;
  x: number | null;
  y: number | null;
  heading: number | null;
  videoFeedUrl: string;
  warningMessage: string;
  // Actions
  fetchDroneInfo: () => Promise<void>;
  takeoff: () => Promise<void>;
  land: () => Promise<void>;
  emergencyStop: () => Promise<void>;
  fetchDroneStatus: () => Promise<void>;
  performSequence: () => Promise<void>;
  abortSequence: () => Promise<void>;
  controlDrone: (direction: string, speed?: number) => Promise<void>;
}

const useDroneStore = create<DroneState>((set, get) => ({
  connected: false,
  info: null,
  isFlying: false,
  sequenceRunning: false,
  flight_time: null,
  batteryLevel: null,
  speed: null,
  distance: null,
  temperature: null,
  altitude: null,
  x: null,
  y: null,
  heading: null,
  videoFeedUrl: droneApi.getVideoFeedUrl(),
  warningMessage: "",

  fetchDroneInfo: async () => {
    try {
      const data = await droneApi.getDroneInfo();
      set({ info: data, connected: true });
    } catch (error) {
      set({ connected: false });
    }
  },

  takeoff: async () => {
    const { batteryLevel } = get();
    if (batteryLevel !== null && batteryLevel < 10) {
      set({ warningMessage: "Battery level is too low to take off." });
      toast.warning("Battery level is too low to take off.");
      return;
    }
    try {
      await droneApi.takeoff();
      set({ isFlying: true, warningMessage: "" });
    } catch (error) {
      toast.error(droneApi.errorMessage(error, "Error taking off."));
    }
  },

  land: async () => {
    try {
      await droneApi.land();
      set({ isFlying: false });
    } catch (error) {
      toast.error(droneApi.errorMessage(error, "Error landing."));
    }
  },

  emergencyStop: async () => {
    try {
      await droneApi.emergencyStop();
      set({ isFlying: false, sequenceRunning: false });
      toast.warning("Emergency stop: motors cut.");
    } catch (error) {
      toast.error(droneApi.errorMessage(error, "Emergency stop failed."));
    }
  },

  fetchDroneStatus: async () => {
    try {
      const data = await droneApi.getStatus();
      if (data.status === "success") {
        set({
          connected: true,
          isFlying: data.is_flying,
          sequenceRunning: data.sequence_running,
          flight_time: data.flight_time,
          batteryLevel: data.battery_level,
          speed: data.speed,
          distance: data.distance,
          temperature: data.temperature,
          altitude: data.altitude,
          x: data.x,
          y: data.y,
          heading: data.heading,
        });
      }
    } catch (error) {
      set({ connected: false });
    }
  },

  performSequence: async () => {
    try {
      await droneApi.performSequence();
      set({ sequenceRunning: true });
    } catch (error) {
      toast.error(droneApi.errorMessage(error, "Could not start sequence."));
    }
  },

  abortSequence: async () => {
    try {
      await droneApi.abortSequence();
    } catch (error) {
      toast.error(droneApi.errorMessage(error, "Could not abort sequence."));
    }
  },

  controlDrone: async (direction, speed = 50) => {
    try {
      await droneApi.control(direction, speed);
    } catch (error) {
      // Fixed id: a held key repeats, so keep a single toast instead of a stack.
      toast.error(
        droneApi.errorMessage(
          error,
          `Error controlling drone (${direction} at speed ${speed})`
        ),
        { id: "control-error" }
      );
    }
  },
}));

export default useDroneStore;
