"use client";
import { Button } from "@/components/ui/button";
import { getVideoFeedUrl, health, land, takeoff } from "@/lib/drone";
import { useState } from "react";

export default function Home() {
  const [isFlying, setIsFlying] = useState(false);

  const handleTakeoff = async () => {
    try {
      await takeoff();
      setIsFlying(true);
    } catch (error) {
      console.error(error);
    }
  };

  const handleHealth = async () => {
    try {
      const response = await health();
      console.log(response);
    } catch (error) {
      console.error(error);
    }
  };

  const handleLand = async () => {
    try {
      await land();
      setIsFlying(false);
    } catch (error) {
      console.error(error);
    }
  };
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <Button onClick={handleTakeoff}>Launch</Button>
      <Button onClick={handleHealth}>HealthChecker</Button>
      <Button onClick={handleLand}>Land</Button>
      {isFlying && (
        <div>
          <h2>Live Video Feed</h2>
          <img
            src={getVideoFeedUrl()}
            alt="Live Video Feed"
            style={{ width: "100%", maxHeight: "500px" }}
          />
        </div>
      )}
    </main>
  );
}
