"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useContext, type ReactNode } from "react";

import { apiRequest, ApiError } from "@/lib/api";
import type { User } from "@/lib/types";

type AuthContextValue = {
  user: User | null;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const query = useQuery({
    queryKey: ["me"],
    queryFn: () => apiRequest<User>("/auth/me"),
    retry: (count, error) => !(error instanceof ApiError && error.status === 401) && count < 1,
  });
  const user = query.data ?? null;

  const setUser = (nextUser: User | null) => {
    queryClient.setQueryData(["me"], nextUser);
  };

  const logout = async () => {
    await apiRequest<void>("/auth/logout", { method: "POST" });
    queryClient.clear();
  };

  return (
    <AuthContext.Provider value={{ user, isLoading: query.isLoading, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}

