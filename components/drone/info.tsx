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
import { Badge } from "../ui/badge";

export default function DroneInfo() {
  const {
    flight_time,
    batteryLevel,
    speed,
    distance,
    temperature,
    altitude,
    x,
    y,
    heading,
    info,
    connected,
    fetchDroneInfo,
    fetchDroneStatus,
  } = useDroneStore();

  useEffect(() => {
    const poll = () => {
      if (!useDroneStore.getState().info) fetchDroneInfo();
      fetchDroneStatus();
    };
    poll();
    const interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, [fetchDroneInfo, fetchDroneStatus]);

  const has = (capability: string) =>
    info?.capabilities.includes(capability) ?? false;
  const unknown = <span>Unknown</span>;
  return (
    <>
      <Card x-chunk="dashboard-01-chunk-5">
        <CardHeader className="flex flex-row items-start bg-muted/50">
          <div className="grid gap-0.5">
            <CardTitle className="group flex items-center gap-2 text-lg">
              {info?.name ?? "Connecting…"}
              {info?.simulated && <Badge variant="secondary">Virtual</Badge>}
              {!connected && <Badge variant="destructive">Offline</Badge>}
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
              {info?.description ?? "Waiting for the drone API…"}
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
                  unknown
                )}
              </li>
              {has("temperature") && (
                <li className="flex items-center justify-between">
                  <span className="text-muted-foreground">Temperature</span>
                  {temperature !== null ? (
                    <span>{temperature} (°C)</span>
                  ) : (
                    unknown
                  )}
                </li>
              )}
              {info?.max_speed != null && (
                <li className="flex items-center justify-between">
                  <span className="text-muted-foreground">Max Speed</span>
                  <span>{info.max_speed} (m/s)</span>
                </li>
              )}
              {info?.max_altitude != null && (
                <li className="flex items-center justify-between">
                  <span className="text-muted-foreground">Max Altitude</span>
                  <span>{info.max_altitude} (m)</span>
                </li>
              )}
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
                  unknown
                )}
              </li>
              <li className="flex items-center justify-between">
                <span className="text-muted-foreground">Speed </span>
                {speed !== null ? (
                  <span>{speed} (m/s)</span>
                ) : (
                  unknown
                )}
              </li>
              <li className="flex items-center justify-between">
                <span className="text-muted-foreground">Altitude</span>
                {altitude !== null ? (
                  <span>{altitude} (m)</span>
                ) : (
                  unknown
                )}
              </li>
              {has("position") && (
                <li className="flex items-center justify-between">
                  <span className="text-muted-foreground">Position</span>
                  {x !== null && y !== null ? (
                    <span>
                      {x}, {y} (m){heading !== null && ` · ${heading}°`}
                    </span>
                  ) : (
                    unknown
                  )}
                </li>
              )}
              {has("tof_sensor") && (
                <li className="flex items-center justify-between">
                  <span className="text-muted-foreground">
                    Obstacle Distance
                  </span>
                  {distance !== null ? <span>{distance} (m)</span> : unknown}
                </li>
              )}
            </ul>
          </div>
        </CardContent>
      </Card>
    </>
  );
}
