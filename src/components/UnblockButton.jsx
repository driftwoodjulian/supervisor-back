"use client"

import { useState } from "react"

const UnblockButton = ({ ip, srv , user}) => {
    const [sent, setSent] = useState(false)
    const [error, setError] = useState(null)
    const [sending, setSending] = useState(false)
        


    const token = localStorage.getItem("palatron_jwt")

    const handlequery = async (e) => {
        setSending(true)
        setError(null)
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_UNBLOCK_ENDPOINT}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    srv: srv.trim(),
                    ip: ip.trim(),
                    username: user,
                }),
            })

            const data = await response.json()
            console.log(data)
            setSent(true)
        } catch(err) {
            console.log(err)
            setError("Hubo un error ejecutando el comando")
        } finally {
            setSending(false)
        }
    }
    let thing = null
    if(!sent && !error){
        thing= <button onClick={handlequery} className="btn btn-warning">Desbloquear {ip}</button>        
    }else if(sending){
        thing = <p className="text-white">...enviando peticion</p>
    }else if (error){
        setSent(false)
        thing = <button onClick={handlequery} className="btn btn-danger">Tratar de nuevo?</button>, <p>{error}</p>

    }else if(sent && !error){
        thing = <button className="btn btn-secondary"> Se desbloqueo </button>
    }

    return thing//<button onClick={handlequery} className="btn btn-warning">Desbloquear {ip}</button>
}

export default UnblockButton