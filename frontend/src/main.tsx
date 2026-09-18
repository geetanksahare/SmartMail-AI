import React from "react";
import ReactDOM from "react-dom/client";

import {
  BrowserRouter,
} from "react-router";

import {
  QueryClientProvider,
} from "@tanstack/react-query";

import App from "./App";

import {
  AuthProvider,
} from "./context/AuthContext";

import {
  queryClient,
} from "./lib/queryClient";

import "./styles.css";

ReactDOM.createRoot(
  document.getElementById(
    "root",
  )!,
).render(
  <React.StrictMode>
    <QueryClientProvider
      client={queryClient}
    >
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
);