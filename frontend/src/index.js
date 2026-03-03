import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { Capacitor } from "@capacitor/core";
import { SplashScreen } from "@capacitor/splash-screen";
import { StatusBar, Style } from "@capacitor/status-bar";

const initializeApp = async () => {
  if (Capacitor.isNativePlatform()) {
    try {
      await StatusBar.setStyle({ style: Style.Dark });
      await StatusBar.setBackgroundColor({ color: "#111827" });
    } catch (e) {
      // StatusBar plugin not available on this platform
    }
    try {
      await SplashScreen.hide();
    } catch (e) {
      // SplashScreen plugin not available
    }
  }
};

const root = ReactDOM.createRoot(document.getElementById("root"));

initializeApp().then(() => {
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
});
