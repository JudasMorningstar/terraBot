import useDroneStore from "@/lib/store/drone-store";
import { Button } from "../ui/button";
import { useEffect } from "react";

export default function DroneControls() {
  const {
    takeoff,
    land,
    emergencyStop,
    performSequence,
    abortSequence,
    sequenceRunning,
    controlDrone,
  } = useDroneStore();

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Don't fly the drone while the user is typing in a form field.
      const target = event.target as HTMLElement | null;
      if (
        target &&
        (target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.isContentEditable)
      ) {
        return;
      }

      switch (event.key) {
        case "ArrowUp":
          event.preventDefault();
          controlDrone("forward");
          break;
        case "ArrowDown":
          event.preventDefault();
          controlDrone("backward");
          break;
        case "ArrowLeft":
          event.preventDefault();
          controlDrone("left");
          break;
        case "ArrowRight":
          event.preventDefault();
          controlDrone("right");
          break;
        case "w":
          controlDrone("up");
          break;
        case "s":
          controlDrone("down");
          break;
        case "a":
          controlDrone("ccw");
          break;
        case "d":
          controlDrone("cw");
          break;
        case "e":
          if (!event.repeat) takeoff();
          break;
        case "q":
          if (!event.repeat) land();
          break;
        default:
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [controlDrone, takeoff, land]);

  return (
    <div className="flex w-full flex-wrap gap-4 justify-between">
      <Button className="flex-1" onClick={takeoff}>
        Launch
      </Button>
      {sequenceRunning ? (
        <Button className="flex-1" variant="secondary" onClick={abortSequence}>
          Abort Sequence
        </Button>
      ) : (
        <Button className="flex-1" onClick={performSequence}>
          Perform Sequence
        </Button>
      )}
      <Button className="flex-1" onClick={land}>
        Land
      </Button>
      <Button
        className="flex-1"
        variant="destructive"
        onClick={emergencyStop}
        title="Cuts the motors immediately: the drone will fall"
      >
        Emergency Stop
      </Button>
    </div>
  );
}
