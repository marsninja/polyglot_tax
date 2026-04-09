import { useState, useEffect } from "react";
import type { Todo } from "./types";

function App() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [text, setText] = useState("");

  useEffect(() => {
    fetch("/api/get_todos")
      .then((r) => r.json())
      .then(setTodos);
  }, []);

  async function add() {
    if (!text.trim()) return;
    const res = await fetch("/api/add_todo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: text.trim() }),
    });
    const todo: Todo = await res.json();
    setTodos([...todos, todo]);
    setText("");
  }

  return (
    <div>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") add();
        }}
        placeholder="Add a todo..."
      />
      <button onClick={add}>Add</button>
      {todos.map((t) => (
        <p key={t.id}>
          {t.title} ({t.category})
        </p>
      ))}
    </div>
  );
}

export default App;
