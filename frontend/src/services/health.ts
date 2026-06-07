import { api } from "@/lib/api";

export const healthService = {
  check: () => api.get<{ status: string; service: string; version: string }>("/health"),
};
