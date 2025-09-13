import React from "react";
import TasksList from "./components/TasksList";
import Submissions from "./components/Submissions";

export default function App(){
  return (
    <div style={{padding:20}}>
      <h1>Panda Technic Tasks — Admin</h1>
      <TasksList />
      <hr/>
      <Submissions />
    </div>
  )
}
