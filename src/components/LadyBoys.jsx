import React, { useState, useEffect } from 'react';
import img1 from '../ladyboys/Screenshot from 2026-01-27 15-23-30.png';
import img2 from '../ladyboys/Screenshot from 2026-01-27 15-24-24.png';
import img3 from '../ladyboys/Screenshot from 2026-01-27 15-25-12.png';
import img4 from '../ladyboys/Screenshot from 2026-01-27 15-26-03.png';

const LadyBoys = () => {
    const [profiles, setProfiles] = useState([]);

    useEffect(() => {
        const images = [img1, img2, img3, img4];

        const initialProfiles = [
            { name: "lucho", phone: "54 9 11 6507-1674" },
            { name: "nahu", phone: "54 9 11 5692-1524" },
            { name: "kurchan", phone: "54 9 11 3945-6088" },
            { name: "lucas", phone: "54 9 11 3030-0045" }
        ];

        // Shuffle images randomly
        const shuffledImages = [...images].sort(() => 0.5 - Math.random());

        // Assign shuffled images to profiles
        const assignedProfiles = initialProfiles.map((profile, index) => ({
            ...profile,
            image: shuffledImages[index]
        }));

        setProfiles(assignedProfiles);
    }, []);

    return (
        <div className="container mt-4">
            <h2 className="text-white mb-4">Lady Boys</h2>
            <div className="row">
                {profiles.map((profile, index) => (
                    <div key={index} className="col-md-3 mb-4">
                        <div className="card h-100 bg-dark text-white border-secondary">
                            <div style={{ height: '300px', overflow: 'hidden' }}>
                                <img
                                    src={profile.image}
                                    className="card-img-top"
                                    alt={profile.name}
                                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                />
                            </div>
                            <div className="card-body">
                                <h5 className="card-title text-capitalize text-warning">{profile.name}</h5>
                                <p className="card-text text-light">
                                    <i className="bi bi-telephone me-2"></i>
                                    {profile.phone}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default LadyBoys;
