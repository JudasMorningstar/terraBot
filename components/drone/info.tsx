"use client";

import { Separator } from "@radix-ui/react-select";
import { Copy } from "lucide-react";
import React, { useEffect } from "react";
import { Button } from "../ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "../ui/card";
import useDroneStore from "@/lib/store/drone-store";

export default function DroneInfo() {
  const {
    flight_time,
    batteryLevel,
    speed,
    distance,
    temperature,
    altitude,
    fetchDroneStatus,
  } = useDroneStore();

  useEffect(() => {
    const interval = setInterval(() => {
      fetchDroneStatus();
    }, 5000); // Fetch drone status every 5 seconds
    return () => clearInterval(interval);
  }, [fetchDroneStatus]);
  return (
    <>
      <Card x-chunk="dashboard-01-chunk-5">
        <CardHeader className="flex flex-row items-start bg-muted/50">
          <div className="grid gap-0.5">
            <CardTitle className="group flex items-center gap-2 text-lg">
              DJI Tello
              <Button
                size="icon"
                variant="outline"
                className="h-6 w-6 opacity-0 transition-opacity group-hover:opacity-50"
              >
                <Copy className="h-3 w-3" />
                <span className="sr-only">Copy Drone Name</span>
              </Button>
            </CardTitle>
            <CardDescription>
              The DJI Tello is a compact, beginner-friendly drone with a 5MP
              camera.
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="p-6 text-sm">
          <div className="grid gap-3">
            <div className="font-semibold">Drone Info</div>
            <ul className="grid gap-3">
              <li className="flex items-center justify-between">
                <span className="text-muted-foreground">Battery Status</span>
                {batteryLevel !== null ? (
                  <span>{batteryLevel}%</span>
                ) : (
                  <span>Unkown</span>
                )}
              </li>
              <li className="flex items-center justify-between">
                <span className="text-muted-foreground">Temperature</span>
                {temperature !== null ? (
                  <span>{temperature} (°C)</span>
                ) : (
                  <span>Unkown</span>
                )}
              </li>
              <li className="flex items-center justify-between">
                <span className="text-muted-foreground">Max Speed</span>

                <span>0,5 (m/s)</span>
              </li>
              <li className="flex items-center justify-between">
                <span className="text-muted-foreground">Max Altitude</span>
                <span>10 (m)</span>
              </li>
            </ul>
            <Separator className="my-2" />
          </div>

          <Separator className="my-4" />
          <div className="grid gap-3">
            <div className="font-semibold">Flight Information</div>
            <ul className="grid gap-3">
              <li className="flex items-center justify-between">
                <span className="text-muted-foreground">Flight Time</span>

                {flight_time !== null ? (
                  <span>{flight_time} (s)</span>
                ) : (
                  <span>Unkown</span>
                )}
              </li>
              <li className="flex items-center justify-between">
                <span className="text-muted-foreground">Speed </span>
                {speed !== null ? (
                  <span>{speed} (m/s)</span>
                ) : (
                  <span>Unkown</span>
                )}
              </li>
              <li className="flex items-center justify-between">
                <span className="text-muted-foreground">Altitude</span>
                {altitude !== null ? (
                  <span>{altitude} (m)</span>
                ) : (
                  <span>Unkown</span>
                )}
              </li>
              <li className="flex items-center justify-between">
                <span className="text-muted-foreground">Total Distance</span>
                {distance !== null ? (
                  <span>{distance} (m/s)</span>
                ) : (
                  <span>Unkown</span>
                )}
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </>
  );
}
