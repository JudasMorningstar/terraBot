import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../ui/card";
import Image from "next/image";
import useDroneStore from "@/lib/store/drone-store";
import { Button } from "../ui/button";
import { AspectRatio } from "../ui/aspect-ratio";
import { Skeleton } from "../ui/skeleton";
import { toast } from "sonner";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { Terminal } from "lucide-react";

export default function LiveFeed() {
  const { isFlying, batteryLevel, takeoff, land, videoFeedUrl } =
    useDroneStore();

  return (
    <>
      <img
        className="rounded-md"
        src={videoFeedUrl}
        alt="Live Video Feed"
        style={{ width: "100%", maxHeight: "100%" }}
      />
    </>
  );
}
