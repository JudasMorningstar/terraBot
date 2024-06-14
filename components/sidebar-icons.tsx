"use client";

import Link from "next/link";
import React from "react";
import { Icons } from "./icons";
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip";
import { useSelectedLayoutSegment } from "next/navigation";
import { NavItem } from "@/types";
import { cn } from "@/lib/utils";

export interface SideBarIconsProps {
  items: NavItem[];
}

function SideBarIcons({ items }: SideBarIconsProps) {
  const segment = useSelectedLayoutSegment();
  if (!items?.length) return null;
  return (
    <div>
      <nav className="flex flex-col items-center gap-4 px-2 sm:py-4">
        <Link
          href="#"
          className="group flex h-9 w-9 shrink-0 items-center justify-center gap-2 rounded-full bg-primary text-lg font-semibold text-primary-foreground md:h-8 md:w-8 md:text-base"
        >
          <Icons.logo className="h-4 w-4 transition-all group-hover:scale-110" />
          <span className="sr-only">TerraBot</span>
        </Link>
        {items.map((item, index) => {
          const Icon = item.icon ? Icons[item.icon] : Icons.home;
          return item.href ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Link
                  href={item.href}
                  className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground md:h-8 md:w-8"
                >
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right">{item.title}</TooltipContent>
            </Tooltip>
          ) : (
            <span
              key={index}
              className="flex w-full cursor-not-allowed items-center rounded-md p-2 text-muted-foreground hover:underline"
            >
              {item.title}
            </span>
          );
        })}
      </nav>
      <nav className="mt-auto flex flex-col items-center gap-4 px-2 py-4">
        <Tooltip>
          <TooltipTrigger asChild>
            <Link
              href="#"
              className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground md:h-8 md:w-8"
            >
              <Icons.settings className="h-5 w-5" />
              <span className="sr-only">Settings</span>
            </Link>
          </TooltipTrigger>
          <TooltipContent side="right">Settings</TooltipContent>
        </Tooltip>
      </nav>
    </div>
  );
}

export default SideBarIcons;
