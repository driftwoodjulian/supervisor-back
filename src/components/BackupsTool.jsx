"use client"

import { useState } from "react"

const BackupsTool = ({ user }) => {
  const [server, setServer] = useState("")
  const [client, setClient] = useState("")
  const [responses, setResponses] = useState([])
  const [loading, setLoading] = useState(false)

  const handleQuery = async (e) => {
    e.preventDefault()
    if (!server.trim() || !client.trim()) return

    setLoading(true)
    const token = localStorage.getItem("palatron_jwt")

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_BACKUPS_ENDPOINT}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user: user.username,
          srv: server.trim(),
          client: client.trim(),
        }),
      })

      const data = await response.json()
      console.log(data)
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
        client: client.trim(),
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
      <h3 className="text-white mb-4">BACKUPS Tool</h3>
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
              <label htmlFor="client" className="form-label text-white">
                Client Name
              </label>
              <input
                type="text"
                className="form-control"
                id="client"
                value={client}
                onChange={(e) => setClient(e.target.value)}
                placeholder="Enter client name"
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
                  "Check Backups"
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
                  Server: {response.server} | Client: {response.client}
                </strong>
                <small className="text-light">{response.timestamp}</small>
              </div>
              <div className="text-light">
                <strong>Status:</strong> {response.status}
              </div>
              <div className="text-light mt-1">
                {response.isError ? (
                  <span className="text-danger">{response.data}</span>
                ) : (
                  <pre className="text-info mb-0" style={{ whiteSpace: "pre-wrap" }}>
                    {
                      response.data ? response.data : "La busqueda se completo pero parece que no se encontro un backup en el dagon de ese servidor, puede que no exista o que se halla desconectado el servicio de backups del server"
                    }
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

export default BackupsTool

