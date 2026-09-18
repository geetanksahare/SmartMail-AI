import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import type {
  ReactNode,
} from "react";

import {
  clearAccessToken,
  getAccessToken,
  login as apiLogin,
  register as apiRegister,
  setAccessToken,
} from "../lib/api";

interface AuthContextValue {
  token: string | null;
  isAuthenticated: boolean;

  signIn(
    email: string,
    password: string,
  ): Promise<void>;

  signUp(
    name: string,
    email: string,
    password: string,
  ): Promise<void>;

  signOut(): void;
}

const AuthContext =
  createContext<AuthContextValue | null>(
    null,
  );

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [token, setToken] =
    useState<string | null>(
      getAccessToken(),
    );

  useEffect(() => {
    function handleExpired() {
      clearAccessToken();
      setToken(null);
    }

    window.addEventListener(
      "smartmail:auth-expired",
      handleExpired,
    );

    return () => {
      window.removeEventListener(
        "smartmail:auth-expired",
        handleExpired,
      );
    };
  }, []);

  async function signIn(
    email: string,
    password: string,
  ) {
    const result =
      await apiLogin(
        email,
        password,
      );

    setAccessToken(
      result.access_token,
    );

    setToken(
      result.access_token,
    );
  }

  async function signUp(
    name: string,
    email: string,
    password: string,
  ) {
    await apiRegister(
      name,
      email,
      password,
    );

    await signIn(
      email,
      password,
    );
  }

  function signOut() {
    clearAccessToken();
    setToken(null);
  }

  const value =
    useMemo<AuthContextValue>(
      () => ({
        token,
        isAuthenticated:
          Boolean(token),
        signIn,
        signUp,
        signOut,
      }),
      [token],
    );

  return (
    <AuthContext.Provider
      value={value}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context =
    useContext(
      AuthContext,
    );

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider.",
    );
  }

  return context;
}