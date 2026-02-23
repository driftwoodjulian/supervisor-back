import React from "react";

function BackupList({ data }) {
    if (!data || !Array.isArray(data)) return null;
  
    const suspended = data[0]?.suspended || [];
    const active = data[1]?.active || [];
    const count = data[2]?.count ?? 0;
  
    const renderItem = (item, idx) => {
      if (!item.backup) {
        return (
          <li key={idx} className="text-danger">
            <strong>{item.user}</strong> – <em>No backup available</em>
          </li>
        );
      }
  
      return (
        <li key={idx}>
          <strong>{item.user}</strong> ––––  {'>  '+item.backup.file+"    "}    
          (size: {item.backup.size + " bytes"}, Ultima modificacion del archivo: {item.backup.mtime})
        </li>
      );
    };
  
    return (
      <div>
        <h2>Suspended ({suspended.length})</h2>
        <ul className="text-warning">
          {suspended.map(renderItem)}
        </ul>
  
        <h2>Active ({active.length})</h2>
        <ul className="text-white">
          {active.map(renderItem)}
        </ul>
  
        <p>Total count: {count}</p>
      </div>
    );
  }

export default BackupList;