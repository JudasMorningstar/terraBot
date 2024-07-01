import { Icons } from "@/components/icons";

export interface NavItem {
  title: string;
  href: string;
  icon?: keyof typeof Icons;
}

export interface DroneState {
  isFlying: boolean;
  flight_time: number | null;
  batteryLevel: number | null;
  speed: number | null;
  distance: number | null;
  temperature: number | null;
  altitude: number | null;
  videoFeedUrl: string;
  warningMessage: string;
  performSequence: () => Promise<void>;
  takeoff: () => Promise<void>;
  land: () => Promise<void>;
  fetchDroneStatus: () => Promise<void>;
}
