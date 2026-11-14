import React from "react";
import useDroneStore from "@/lib/store/drone-store";
import { Badge } from "../ui/badge";

export default function LiveFeed() {
  const { videoFeedUrl, connected } = useDroneStore();

  return (
    <div className="relative h-full w-full">
      {/* MJPEG stream: a plain <img> is the simplest way to display it. */}
      <img
        className="rounded-md"
        src={videoFeedUrl}
        alt="Live Video Feed"
        style={{ width: "100%", maxHeight: "100%" }}
      />
      <div className="absolute left-2 top-2 flex gap-2">
        {!connected && <Badge variant="destructive">No connection</Badge>}
      </div>
    </div>
  );
}
