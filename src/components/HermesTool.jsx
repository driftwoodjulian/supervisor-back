"use client"

import { useState } from "react"
import  BackupList  from "./BackupList"

const HermesTool = ({ user }) => {
  const [server, setServer] = useState("")
  const [responses, setResponses] = useState([])
  const [loading, setLoading] = useState(false)

  const handleQuery = async (e) => {
    e.preventDefault()
    if (!server.trim()) return

    setLoading(true)
    const token = localStorage.getItem("palatron_jwt")

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_HERMES_ENDPOINT}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user: user.username,
          srv: server.trim(),
        }),
      })

      

      const data = await response.json()
      console.log(data)
      console.log(data.data)
      console.log(data.data)
      console.log(data.error)
      const timestamp = new Date().toLocaleString()

      const newResponse = data.error
        ? {
            id: Date.now(),
            timestamp,
            server: server.trim(),
            status: response.status,
            data: data.error,
            isError: response.status !== 200,
          }
        : {
            id: Date.now(),
            timestamp,
            server: server.trim(),
            status: response.status,
            data: data.data,
            isError: response.status !== 200,
          }
      console.log(newResponse)
      setResponses((prev) => [newResponse, ...prev])
    } catch (error) {
      const timestamp = new Date().toLocaleString()
      const newResponse = {
        id: Date.now(),
        timestamp,
        server: server.trim(),
        status: "ERROR",
        data: { error: "Connection failed" },
        isError: true,
      }
      setResponses((prev) => [newResponse, ...prev])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="tool-section">
      <h3 className="text-white mb-4">Hermes Tool</h3>
      <form onSubmit={handleQuery}>
        <div className="row">
          <div className="col-md-8">
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
              <label className="form-label text-white">&nbsp;</label>
              <button type="submit" className="btn btn-warning w-100" disabled={loading}>
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Querying...
                  </>
                ) : (
                  "Query"
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
                <strong className="text-white">Server: {response.server}</strong>
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
                    
                    <BackupList
                    data={response.data}
                    />
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

export default HermesTool

