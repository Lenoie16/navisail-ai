import type { Metadata } from "next";
import "../styles/globals.css";
import { RealtimeProvider } from "../components/realtime-provider";

export const metadata: Metadata = {
  title: "Navisail AI",
  description: "Maritime logistics decision intelligence",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <RealtimeProvider>{children}</RealtimeProvider>
      </body>
    </html>
  );
}
