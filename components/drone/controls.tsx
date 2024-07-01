import { takeoff, land } from "@/lib/drone";
import useDroneStore from "@/lib/store/drone-store";
import { Button } from "../ui/button";
import { useEffect } from "react";

export default function DroneControls() {
  const { takeoff, land, performSequence, controlDrone } = useDroneStore();
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case "ArrowUp":
          controlDrone("forward");
          break;
        case "ArrowDown":
          controlDrone("backward");
          break;
        case "ArrowLeft":
          controlDrone("left");
          break;
        case "ArrowRight":
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
          takeoff();
          break;
        case "q":
          land();
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
    <div className="flex gap-4 justify-between w-full">
      <Button className="w-full" onClick={takeoff}>
        Launch
      </Button>
      {/* {isFlying &&} */}
      <Button className="w-full" onClick={performSequence}>
        Perform Sequnce
      </Button>
      <Button className="w-full" onClick={land}>
        Land
      </Button>
    </div>
  );
}
