import type { NavItem } from "@/types";

export interface SiteConfigProps {
  sidebarNav: NavItem[];
}

export const siteConfig: SiteConfigProps = {
  sidebarNav: [
    {
      title: "Home",
      href: "/",
      icon: "home",
    },
    {
      title: "Gallery",
      href: "/gallery",
      icon: "gallery",
    },
    {
      title: "Map",
      href: "/map",
      icon: "map",
    },
    {
      title: "Notifications",
      href: "/notifications",
      icon: "notification",
    },
  ],
};
