import React from "react";
import { Sheet, SheetContent, SheetTrigger } from "./ui/sheet";
import { PanelLeft } from "lucide-react";
import { Button } from "./ui/button";
import { NavItem } from "@/types";
import Link from "next/link";
import { Icons } from "./icons";

export interface MobileNavProps {
  items: NavItem[];
}

export default function MobileNav({ items }: MobileNavProps) {
  return (
    <>
      <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
        <Sheet>
          <SheetTrigger asChild>
            <Button size="icon" variant="outline" className="sm:hidden">
              <PanelLeft className="h-5 w-5 text-primary-foreground" />
              <span className="sr-only">Toggle Menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="sm:max-w-xs">
            <nav className="grid gap-6 text-lg font-medium">
              <Link
                href="/"
                className="group flex h-10 w-10 shrink-0 items-center justify-center gap-2 rounded-full bg-primary text-lg font-semibold text-primary-foreground md:text-base"
              >
                <Icons.logo className="h-5 w-5 transition-all group-hover:scale-110" />
                <span className="sr-only">TerraBot</span>
              </Link>
              {items.map((item) => {
                const Icon = item.icon ? Icons[item.icon] : Icons.home;
                return item.href ? (
                  <Link
                    href={item.href}
                    className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-primary "
                  >
                    <Icon className="h-5 w-5" aria-hidden="true" />
                    {item.title}
                  </Link>
                ) : (
                  <span>{item.title}</span>
                );
              })}
            </nav>
          </SheetContent>
        </Sheet>
      </header>
    </>
  );
}