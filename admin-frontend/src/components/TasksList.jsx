import React, {useState, useEffect} from "react";
import api from "../api";

export default function TasksList(){
  const [tasks, setTasks] = useState([]);
  const [name,setName] = useState("");
  const [link,setLink] = useState("");
  const [desc,setDesc] = useState("");

  useEffect(()=>{ fetchTasks() },[]);

  async function fetchTasks(){
    try{
      const res = await fetch(`${process.env.REACT_APP_BACKEND_URL || "http://localhost:5000"}/api/tasks`);
      const js = await res.json();
      setTasks(js);
    }catch(e){ console.error(e) }
  }

  async function addTask(){
    try{
      await api.post("/api/admin/tasks/add", { name, link, description: desc });
      setName(""); setLink(""); setDesc("");
      fetchTasks();
    }catch(e){ alert("Failed to add task. Check admin token.") }
  }

  return (
    <div>
      <h2>Tasks</h2>
      <div>
        <input placeholder="Name" value={name} onChange={e=>setName(e.target.value)} />
        <input placeholder="Link" value={link} onChange={e=>setLink(e.target.value)} />
        <input placeholder="Description" value={desc} onChange={e=>setDesc(e.target.value)} />
        <button onClick={addTask}>Add Task</button>
      </div>
      <ul>
        {tasks.map(t=> <li key={t.id}><b>{t.name}</b> — {t.link}</li>)}
      </ul>
    </div>
  )
}
