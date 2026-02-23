"use client"

import { useState } from "react"
import UnblockButton  from "./UnblockButton"
const WhmTool = ({ user }) => {
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
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_UNBLOCK_WHM_ENDPOINT}`, {
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
      console.log("el err: "+err)

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
      <h3 className="text-white mb-4">Whm Tool</h3>
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

export default WhmTool

