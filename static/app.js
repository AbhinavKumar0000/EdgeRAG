async function upload() {
  let f = document.getElementById("pdf").files[0];
  let fd = new FormData();
  fd.append("file", f);
  await fetch("/upload", { method: "POST", body: fd });
  alert("Indexed");
}

async function ask() {
  let q = document.getElementById("q").value;
  let chat = document.getElementById("chat");
  chat.innerHTML += `<div class="q">${q}</div><div class="a"></div>`;
  let a = chat.lastChild;

  let r = await fetch("/ask", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({question: q})
  });

  const reader = r.body.getReader();
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    a.innerText += new TextDecoder().decode(value);
  }
}

async function clearDB() {
  await fetch("/clear", {method:"POST"});
  document.getElementById("chat").innerHTML = "";
}
