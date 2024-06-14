import { Icons } from "@/components/icons";
import "./_styles/globals.css";
import { Inter } from "next/font/google";
import SideBarIcons from "@/components/sidebar-icons";
import { TooltipProvider } from "@/components/ui/tooltip";
import { siteConfig } from "@/lib/config";
import MobileNav from "@/components/mobile-nav";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "TerraBot",
  description: "take control of your tello drone!",
  author: "@judasmorningstar",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex min-h-screen w-full flex-col bg-muted/50">
          <aside className="fixed inset-y-0 left-0 z-10 hidden w-14 flex-col border-r bg-background sm:flex">
            <TooltipProvider>
              <SideBarIcons items={siteConfig.sidebarNav} />
            </TooltipProvider>
          </aside>
          <div className="flex flex-col sm:gap-4 sm:py-4 sm:pl-14">
            <MobileNav items={siteConfig.sidebarNav} />
            {children}
            <Toaster />
            {/* <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6"></header> */}
          </div>
        </div>
      </body>
    </html>
  );
}
