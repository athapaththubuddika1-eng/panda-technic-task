import React, {useState, useEffect} from "react";
import api from "../api";

export default function Submissions(){
  const [subs, setSubs] = useState([]);
  useEffect(()=>{ load() },[]);
  async function load(){
    try{
      const res = await api.get("/api/admin/submissions");
      setSubs(res.data);
    }catch(e){ console.error(e); alert("Failed to load submissions") }
  }
  async function changeStatus(id, status){
    try{
      await api.post(`/api/admin/submissions/${id}/status`, { status });
      load();
    }catch(e){ alert("Failed") }
  }
  return (
    <div>
      <h2>Submissions</h2>
      <table border="1" cellPadding="6">
        <thead><tr><th>ID</th><th>User</th><th>Task</th><th>Proof</th><th>Note</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          {subs.map(s=>(
            <tr key={s.id}>
              <td>{s.id}</td>
              <td>{s.user_telegram_id}</td>
              <td>{s.task?.name}</td>
              <td>{s.proof_url ? <a href={`${process.env.REACT_APP_BACKEND_URL || "http://localhost:5000"}${s.proof_url}`} target="_blank" rel="noreferrer">Open</a> : "—"}</td>
              <td>{s.note}</td>
              <td>{s.status}</td>
              <td>
                <button onClick={()=>changeStatus(s.id,"approved")}>Approve</button>
                <button onClick={()=>changeStatus(s.id,"rejected")}>Reject</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
