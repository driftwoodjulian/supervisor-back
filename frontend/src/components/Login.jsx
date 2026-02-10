import React, { useState } from 'react';
import { login } from '../api';
import { setToken } from '../auth';

const Login = ({ onLoginSuccess }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const result = await login(username, password);
            if (result.token) {
                setToken(result.token);
                onLoginSuccess();
            } else {
                console.error('Authentication Failed');
                // Could set a state variable to show error message in UI
            }
        } catch (error) {
            console.error('Connection Error', error);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card p-4">
                <h2 className="login-title">SUPERVISOR AI</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <input
                            type="text"
                            className="form-control"
                            placeholder="IDENTIFIER"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                    </div>
                    <div className="mb-3">
                        <input
                            type="password"
                            className="form-control"
                            placeholder="ACCESS_CODE"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <button type="submit" className="btn btn-primary w-100">AUTHENTICATE</button>
                </form>
            </div>
        </div>
    );
};

export default Login;
