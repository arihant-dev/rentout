const NGROK = "https://sanely-deathless-kemberly.ngrok-free.dev";
const cors = require('cors');

app.use(cors({
  origin: "http://localhost:3000",   // or "http://localhost:3000"
  methods: "*",
  credentials: true
}));
document.getElementById("sendBtn").addEventListener("click", async () => {
    const input = document.getElementById("input").value;

    const response = await fetch(`${NGROK}/api/predict`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: input })
    });

    const data = await response.json();
    document.getElementById("output").innerText = JSON.stringify(data, null, 2);
});
