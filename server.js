// server.js
require("dotenv").config();
const express = require("express");
const multer = require("multer");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 5000;

const upload = multer({ dest: "uploads/" });

app.post("/transcribe", upload.single("audio"), (req, res) => {
  const audioPath = req.file.path;

  const python = spawn("python", ["transcribe.py", audioPath]);

  let output = "";
  python.stdout.on("data", (data) => {
    output += data.toString();
  });

  python.stderr.on("data", (data) => {
    console.error("stderr:", data.toString());
  });

  python.on("close", (code) => {
    // Clean up uploaded file
    fs.unlinkSync(audioPath);
    res.json({ transcription: output.trim() });
  });
});

app.listen(PORT, () => {
  console.log(`🧠 Whisper backend running at http://localhost:${PORT}`);
});
