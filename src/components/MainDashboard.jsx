"use client"

import { useState } from "react"
import CargaTool from "./CargaTool"
import IPTool from "./IPTool"
import BackupsTool from "./BackupsTool"
import HermesTool from "./HermesTool"
import WhmTool from "./WhmTool"
import PasswordTool from "./PasswordChanger"
import LadyBoys from "./LadyBoys"

const MainDashboard = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState("welcome")

  const renderContent = () => {
    switch (activeTab) {
      case "carga":
        return <CargaTool user={user} />
      case "ip":
        return <IPTool user={user} />
      case "backups":
        return <BackupsTool user={user} />
      case "whm":
        return <WhmTool user={user} />
      case "hermes":
        return <HermesTool user={user} />
      case "claves":
        return <PasswordTool user={user} />
      case "lady":
        return <LadyBoys />

      default:
        return (
          <div className="welcome-section">
            <h2 className="text-white mb-3">Bienvenido, {user.username}!</h2>
            <p className="text-light mb-0">Selecciona una herramienta de arriba. Aguante Boca papa. Pierde Boca pierde mi oficina.</p>
          </div>
        )
    }
  }

  return (
    <>
      <nav className="navbar navbar-expand-lg navbar-dark">
        <div className="container-fluid">
          <span className="navbar-brand">Palatron 5000</span>
          <div className="navbar-nav me-auto">
            <button
              className={`nav-link btn btn-link btn-warning ${activeTab === "welcome" ? "active" : ""}`}
              onClick={() => setActiveTab("welcome")}
            >
              HOME
            </button>
            <button
              className={`nav-link btn btn-link btn-warning ${activeTab === "carga" ? "active" : ""}`}
              onClick={() => setActiveTab("carga")}
            >
              CARGA
            </button>
            <button
              className={`nav-link btn btn-link btn-warning ${activeTab === "ip" ? "active" : ""}`}
              onClick={() => setActiveTab("ip")}
            >
              IP
            </button>
            <button
              className={`nav-link btn btn-link btn-warning ${activeTab === "backups" ? "active" : ""}`}
              onClick={() => setActiveTab("backups")}
            >
              BACKUPS
            </button>
            <button
              className={`nav-link btn btn-link btn-warning ${activeTab === "whm" ? "active" : ""}`}
              onClick={() => setActiveTab("whm")}
            >
              WHM
            </button>
            <button
              className={`nav-link btn btn-link btn-warning ${activeTab === "hermes" ? "active" : ""}`}
              onClick={() => setActiveTab("hermes")}
            >
              HERMES TOOl
            </button>
            <button
              className={`nav-link btn btn-link btn-warning ${activeTab === "claves" ? "active" : ""}`}
              onClick={() => setActiveTab("claves")}
            >
              DATOS DIRECT ADMIN
            </button>
            <button
              className={`nav-link btn btn-link btn-warning ${activeTab === "lady" ? "active" : ""}`}
              onClick={() => setActiveTab("lady")}
            >
              LADY BOYS
            </button>
            <button
              className={`nav-link btn btn-link btn-warning ${activeTab === "lady" ? "active" : ""}`}
              onClick={() => setActiveTab("lady")}
            >
              PALA PLUS PREMIUM
            </button>




          </div>
          <button className="btn btn-outline-warning" onClick={onLogout}>
            Logout
          </button>
        </div>
      </nav>
      <div className="main-content">{renderContent()}</div>
    </>
  )
}

export default MainDashboard

