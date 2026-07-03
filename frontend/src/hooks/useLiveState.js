import { useEffect, useRef, useState } from "react";
import { fetchState } from "../api/client";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

export function useLiveState() {
  const [state, setState] = useState(null);
  const [connection, setConnection] = useState("connecting");
  const reconnectTimer = useRef(null);
  const pollingTimer = useRef(null);
  const socketRef = useRef(null);

  useEffect(() => {
    let mounted = true;

    async function loadInitial() {
      try {
        const nextState = await fetchState();
        if (mounted) setState(nextState);
      } catch {
        if (mounted) setConnection("offline");
      }
    }

    function stopPolling() {
      if (pollingTimer.current) {
        clearInterval(pollingTimer.current);
        pollingTimer.current = null;
      }
    }

    function startPolling() {
      if (pollingTimer.current) return;
      setConnection("polling");
      pollingTimer.current = setInterval(async () => {
        try {
          setState(await fetchState());
          setConnection("polling");
        } catch {
          setConnection("offline");
        }
      }, 5000);
    }

    function connect() {
      setConnection((current) => (current === "polling" ? "polling" : "connecting"));
      const socket = new WebSocket(WS_URL);
      socketRef.current = socket;

      socket.onopen = () => {
        stopPolling();
        if (mounted) setConnection("connected");
      };

      socket.onmessage = (event) => {
        if (!mounted) return;
        setState(JSON.parse(event.data));
        setConnection("connected");
      };

      socket.onerror = () => {
        if (mounted) startPolling();
      };

      socket.onclose = () => {
        if (!mounted) return;
        startPolling();
        reconnectTimer.current = setTimeout(connect, 3000);
      };
    }

    loadInitial();
    connect();

    return () => {
      mounted = false;
      stopPolling();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  return { state, connection, setState };
}
