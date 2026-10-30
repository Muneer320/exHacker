import StudioProvider from "@/components/studio/StudioProvider";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <StudioProvider>{children}</StudioProvider>;
}
