"use client"

import { useState } from "react"
import UnblockButton  from "./UnblockButton"
const IPTool = ({ user }) => {
  const [server, setServer] = useState("")
  const [ip, setIp] = useState("")
  const [responses, setResponses] = useState([])
  const [loading, setLoading] = useState(false)


  const handleQuery = async (e) => {
    e.preventDefault()
    if (!server.trim() || !ip.trim()) return

    setLoading(true)
    const token = localStorage.getItem("palatron_jwt")

    let currentOb = null

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_IP_CHECK_ENDPOINT}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          srv: server.trim(),
          ip: ip.trim(),
          username: user.username,
        }),
      })

      const data = await response.json()
      const timestamp = new Date().toLocaleString()
      currentOb = data
      console.log(data)
      console.log(response.status)
      
      const newResponse = data.error
        ? {
            id: Date.now(),
            timestamp,
            server: server.trim(), ip: ip.trim(),
            status: response.status,
            data: data.error,
            isError: response.status !== 200,
          }
        : {
            id: Date.now(),
            timestamp,
            server: server.trim(), ip: ip.trim(),
            status: response.status,
            data: data.data,
            isError: response.status !== 200,
          }

      setResponses((prev) => [newResponse, ...prev])
    } catch (err) {
      console.log("el err: "+currentOb)

      const timestamp = new Date().toLocaleString()
      const newResponse = {
        id: Date.now(),
        timestamp,
        server: server.trim(),
        ip: ip.trim(),
        status: "ERROR",
        data: "aaaaaaaaaaaaaaa",
        isError: true,
      }
      setResponses((prev) => [newResponse, ...prev])


    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="tool-section">
      <h3 className="text-white mb-4">IP Tool</h3>
      <form onSubmit={handleQuery}>
        <div className="row">
          <div className="col-md-4">
            <div className="mb-3">
              <label htmlFor="server" className="form-label text-white">
                Server
              </label>
              <input
                type="text"
                className="form-control"
                id="server"
                value={server}
                onChange={(e) => setServer(e.target.value)}
                placeholder="Enter server name"
                required
              />
            </div>
          </div>
          <div className="col-md-4">
            <div className="mb-3">
              <label htmlFor="ip" className="form-label text-white">
                IP Address
              </label>
              <input
                type="text"
                className="form-control"
                id="ip"
                value={ip}
                onChange={(e) => setIp(e.target.value)}
                placeholder="Enter IP address"
                required
              />
            </div>
          </div>
          <div className="col-md-4">
            <div className="mb-3">
              <label className="form-label text-white">&nbsp;</label>
              <button type="submit" className="btn btn-warning w-100" disabled={loading}>
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Checking...
                  </>
                ) : (
                  "Check IP"
                )}
              </button>
            </div>
          </div>
        </div>
      </form>

      {responses.length > 0 && (
        <div className="response-log">
          <h5 className="text-white mb-3">Response Log</h5>
          {responses.map((response) => (
            <div key={response.id} className={`response-item ${response.isError ? "error" : "success"}`}>
              <div className="d-flex justify-content-between align-items-start mb-2">
                <strong className="text-white">
                  Server: {response.server} | IP: {response.ip}
                </strong>
                <small className="text-light">{response.timestamp}</small>
              </div>
              <div className="text-light">
                <strong>Status:</strong> {response.status}
              </div>
              <div className="text-light mt-1">
                {response.isError ? (
                  <span className="text-danger">Error: {response.data}</span>
                ) : (
                  <pre className="text-info mb-0" style={{ whiteSpace: "pre-wrap" }}>
                    <p className="text-warning mb-0">Mensaje: </p>
                    {JSON.stringify(response.data.message, null, 2)}
                    <p className="text-warning mb-0">listado del blacklist del firewall:</p>
                    {JSON.stringify(response.data.csf_deny_log)}
                    <p className="text-warning mb-0">log del lfd "historial de la ip":</p>
		    {response?.data?.lfd_log
  ? JSON.stringify(response.data.lfd_log)
      .split('\\n')
      .map((line, index) => (
        <p key={index} className="text-light mb-1">
          {line}
        </p>
      ))
  : <p className="text-light mb-1">No log data available.</p>
}



		    <p className="text-white mb-3">Opciones:</p>
                    {response.data.message == "Encontrada en csf.deny y se puede ejecutar un csf -dr" ? <UnblockButton ip={response.ip} user={user.username} srv={response.server}></UnblockButton> : <p className="text-white">No se puede desbloquear {response.ip}</p> }
                  </pre>
                  
                )}
              </div>
              
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default IPTool

