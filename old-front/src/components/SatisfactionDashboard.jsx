"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import ScoreCard from "./ScoreCard";
import ChatDetailsModal from "./ChatDetailsModal";
import Header from "./Header";
import LoadingSpinner from "./LoadingSpinner";
import ErrorMessage from "./ErrorMessage";
import ScoreDistributionChart from "./ScoreDistributionChart";
import { API_BASE, WS_URL } from "../utils/constants";
import { authenticatedFetch, UnauthorizedError } from "../utils/api";
import { TOKEN_STORAGE_KEY } from "../utils/auth";

export default function SatisfactionDashboard({ user, onLogout }) {
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedChat, setSelectedChat] = useState(null);
  const [chatReason, setChatReason] = useState(null);
  const [chatImprovement, setChatImprovement] = useState(null);
  const [chatKeyMessages, setChatKeyMessages] = useState(null);

  const [chatDetails, setChatDetails] = useState(null);
  const [chatMessages, setChatMessages] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [expandedSections, setExpandedSections] = useState({});

  const toggleSection = (key) => {
    setExpandedSections(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const socketRef = useRef(null);
  const reconnectTimer = useRef(null);

  useEffect(() => {
    connectSocket();

    return () => {
      if (socketRef.current) socketRef.current.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, []);

  const connectSocket = () => {
    setLoading(true);
    setError(null);

    try {
      // Adjust this URL to your backend’s actual address
      const token = localStorage.getItem(TOKEN_STORAGE_KEY);
      const socket = new WebSocket(`${WS_URL}?token=${token}`);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log("✅ Connected to satisfaction WebSocket");
        setLoading(false);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (Array.isArray(data)) {
            // The backend sends arrays of scores
            setScores(data);
          } else if (data.data === "No current chats") {
            setScores([]);
          } else {
            // Handle single message or error object
            console.log("anomaly ")
            console.log(data)
            setScores((prev) => [...prev, data]);
          }
        } catch (err) {
          console.error("Invalid JSON:", err);
        }
      };

      socket.onerror = (err) => {
        console.error("WebSocket error:", err);
        setError("WebSocket connection error");
      };

      socket.onclose = () => {
        console.warn("WebSocket closed. Attempting reconnect in 3s...");
        setError("Disconnected. Reconnecting...");
        reconnectTimer.current = setTimeout(connectSocket, 3000);
      };
    } catch (err) {
      setError("Failed to connect WebSocket");
      setLoading(false);
    }
  };

  const fetchChatDetails = async (chatId, reason, improvement, keyMessages) => {
    try {
      setLoadingDetails(true);
      setSelectedChat(chatId);

      const [chatResponse, messagesResponse] = await Promise.all([
        authenticatedFetch(`${API_BASE}/chats/${chatId}`),
        authenticatedFetch(`${API_BASE}/messages/${chatId}`),
      ]);

      if (!chatResponse.ok || !messagesResponse.ok) {
        throw new Error("Failed to fetch chat details");
      }

      const chatData = await chatResponse.json();
      const messagesData = await messagesResponse.json();


      setChatDetails(chatData);
      setChatMessages(messagesData.conversation || []);
      setChatReason(reason);
      setChatImprovement(improvement);
      setChatKeyMessages(keyMessages);
      const modal = new window.bootstrap.Modal(document.getElementById("chatModal"));
      modal.show();
    } catch (err) {
      if (err instanceof UnauthorizedError) {
        onLogout();
        return;
      }
      alert("Error loading chat details: " + err.message);
    } finally {
      setLoadingDetails(false);
    }
  };

  const groupedScores = useMemo(() => {
    const groups = {
      Great: [],
      Good: [],
      Neutral: [],
      Bad: [],
      Horrible: [],
      Error: [],
      Unknown: []
    };

    scores.forEach((item) => {
      let scoreRaw = item.score?.score || item.score;

      // Check for error first
      if (item.score && typeof item.score === 'object' && 'error' in item.score) {
        groups.Error.push(item);
        return;
      }

      let score = "Unknown";
      if (typeof scoreRaw === 'string') {
        score = scoreRaw.charAt(0).toUpperCase() + scoreRaw.slice(1).toLowerCase();
      }

      if (groups.hasOwnProperty(score)) {
        groups[score].push(item);
      } else {
        groups.Unknown.push(item);
      }
    });

    return groups;
  }, [scores]);

  // Section configuration to ensure order
  const sections = [
    { key: "Great", title: "Great - Excellent Satisfaction" },
    { key: "Good", title: "Good - Positive Satisfaction" },
    { key: "Neutral", title: "Neutral - Balanced Experience" },
    { key: "Bad", title: "Bad - Requires Attention" },
    { key: "Horrible", title: "Horrible - Critical Issues" },
    { key: "Error", title: "Errors - Processing Failures" },
    { key: "Unknown", title: "Unknown / Other" }
  ];

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error && scores.length === 0) {
    return <ErrorMessage error={error} onRetry={connectSocket} />;
  }
  console.log(scores)

  return (
    <>
      <Header user={user} onLogout={onLogout} />

      {scores.length > 0 && <ScoreDistributionChart scores={scores} />}

      <div className="score-container">
        {scores.length === 0 ? (
          <p className="text-center text-muted">No current chats</p>
        ) : (
          sections.map(({ key, title }) => {
            const groupItems = groupedScores[key];
            if (groupItems.length === 0) return null;

            return (
              <div key={key} className="score-section">
                <div
                  className={`score-section-header`}
                  onClick={() => toggleSection(key)}
                  style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                >
                  <div className="d-flex alignItems-center gap-3">
                    <span className={`score-badge score-${key.toLowerCase()} mb-0`}>{key}</span>
                    <span>{groupItems.length} Chats</span>
                  </div>
                  <span>{expandedSections[key] ? '▼' : '►'}</span>
                </div>
                {expandedSections[key] && (
                  <div className="score-cards-grid">
                    {groupItems.map((item) => (
                      <ScoreCard
                        key={item.chat_id}
                        chatId={item.chat_id}
                        timeSt={item.timestamp}
                        reason={item.score?.reason || "NO SE ENCONTRO EXPLICACION DE PORQUE"}
                        improvement={item.score?.improvement || "Sin sugerencias de mejora"}
                        keyMessages={item.score?.key_messages || []}
                        score={item.score?.score || item.score}
                        timestamp={item.timestamp}
                        onViewDetails={fetchChatDetails}
                        loading={loadingDetails && selectedChat === item.chat_id}
                      />
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      <ChatDetailsModal
        chatId={selectedChat}
        chatDetails={chatDetails}
        chatMessages={chatMessages}
        chatReasons={chatReason}
        chatImprovement={chatImprovement}
        chatKeyMessages={chatKeyMessages}
      />
    </>
  );
}
