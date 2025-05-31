// server/app.js

const express = require("express");
const multer = require("multer");
const path = require("path");
const cors = require("cors");
const fs = require("fs");
const { spawn } = require("child_process");

const app = express();
const port = 3000;

app.use(cors());
app.use(express.static(path.join(__dirname, "..", "public")));

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadDir = path.join(__dirname, "uploads");
    fs.mkdirSync(uploadDir, { recursive: true });
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    // Pertahankan nama file asli, tapi tambahkan timestamp untuk keunikan
    cb(null, Date.now() + "-" + file.originalname);
  },
});

// Multer sekarang juga akan memproses field non-file (seperti outputFormat, processingMode)
const upload = multer({ storage: storage });

// Endpoint untuk mengkonversi gambar
// Gunakan upload.fields([]) jika ada banyak field, atau upload.single() diikuti express.urlencoded()
// Untuk FormData yang berisi file dan teks, Multer akan menempatkan teks di req.body
app.post("/convert", upload.single("image"), (req, res) => {
  if (!req.file) {
    return res
      .status(400)
      .json({ message: "Tidak ada file gambar yang diunggah." });
  }

  // Ambil data dari req.body yang dikirim frontend (outputFormat, processingMode)
  const outputFormat = req.body.outputFormat || "jpg"; // Default ke jpg jika tidak ada
  const processingMode = req.body.processingMode || "grayscale"; // Default ke grayscale

  const originalFilePath = req.file.path;
  const originalFileName = req.file.filename;

  console.log(`[Node.js] File diunggah: ${originalFileName}`);
  console.log(`[Node.js] Format Output yang diminta: ${outputFormat}`);
  console.log(`[Node.js] Mode Pemrosesan yang diminta: ${processingMode}`);

  const pythonScriptPath = path.join(
    __dirname,
    "python_scripts",
    "image_processor.py"
  );

  // PASTE JALUR LENGKAP PYTHON ANDA DI SINI. HARUS MENUNJUK KE `python.exe` DI FOLDER `venv\Scripts\`
  const pythonExecutable =
    "C:\\xampp\\htdocs\\AuraTransform\\server\\python_scripts\\venv\\Scripts\\python.exe"
  // ATAU untuk Linux/macOS:
  // const pythonExecutable = '/Users/YourUser/ai-photo-converter/server/python_scripts/venv/bin/python';

  // Tentukan jalur untuk menyimpan file hasil konversi
  // Nama file hasil sekarang akan menyertakan format output yang diminta
  const baseName = path.parse(originalFileName).name; // Dapatkan nama file tanpa ekstensi
  const convertedFileName = `${baseName}-converted.${outputFormat}`;
  const convertedFilePath = path.join(
    __dirname,
    "converted",
    convertedFileName
  );

  fs.mkdirSync(path.join(__dirname, "converted"), { recursive: true });

  // Panggil skrip Python sebagai child process, teruskan semua argumen
  const pythonProcess = spawn(pythonExecutable, [
    pythonScriptPath,
    originalFilePath,
    convertedFilePath,
    processingMode, // Argumen ke-3: mode pemrosesan (AI)
    outputFormat, // Argumen ke-4: format output
  ]);

  let pythonOutput = "";
  let pythonError = "";

  pythonProcess.stdout.on("data", (data) => {
    pythonOutput += data.toString();
    console.log(`[Python stdout]: ${data.toString().trim()}`);
  });

  pythonProcess.stderr.on("data", (data) => {
    pythonError += data.toString();
    console.error(`[Python stderr]: ${data.toString().trim()}`);
  });

  pythonProcess.on("close", (code) => {
    console.log(`[Node.js] Child process Python exited with code ${code}`);

    // Hapus file asli yang diunggah setelah selesai diproses
    fs.unlink(originalFilePath, (unlinkErr) => {
      if (unlinkErr)
        console.error(`[Node.js] Gagal menghapus file asli: ${unlinkErr}`);
    });

    if (code !== 0) {
      return res.status(500).json({
        message: "Gagal memproses gambar dengan AI.",
        details: pythonError || "Tidak ada output error dari Python.",
      });
    }

    const successLine = pythonOutput
      .split("\n")
      .find((line) => line.startsWith("SUCCESS:"));
    if (successLine) {
      const finalConvertedPath = successLine.replace("SUCCESS:", "").trim();
      // Pastikan file hasil konversi benar-benar ada sebelum dikirim
      fs.access(finalConvertedPath, fs.constants.F_OK, (err) => {
        if (err) {
          console.error(
            `[Node.js] File hasil konversi tidak ditemukan: ${finalConvertedPath}`,
            err
          );
          return res.status(500).json({
            message: "File hasil konversi tidak ditemukan di server.",
          });
        }

        console.log(`[Node.js] Mengirim file hasil: ${finalConvertedPath}`);
        res.sendFile(finalConvertedPath, (err) => {
          if (err) {
            console.error(
              "[Node.js] Gagal mengirim file hasil ke frontend:",
              err
            );
            res
              .status(500)
              .json({ message: "Gagal mengirim gambar hasil konversi." });
          } else {
            console.log("[Node.js] File hasil berhasil dikirim ke frontend.");
            // Hapus file konversi setelah dikirim (opsional, tergantung kebijakan penyimpanan)
            fs.unlink(finalConvertedPath, (unlinkErr) => {
              if (unlinkErr)
                console.error(
                  `[Node.js] Gagal menghapus file konversi: ${unlinkErr}`
                );
            });
          }
        });
      });
    } else {
      res.status(500).json({
        message:
          "AI processing completed, but no success path found in Python output.",
        details: pythonOutput || "Tidak ada output dari Python.",
      });
    }
  });

  pythonProcess.on("error", (err) => {
    console.error(`[Node.js] Gagal memulai child process Python: ${err}`);
    res.status(500).json({
      message: "Internal server error: Gagal menjalankan proses AI.",
      details: err.message,
    });
  });
});

// --- Server Listener ---
app.listen(port, () => {
  console.log(`Server AuraTransform berjalan di http://localhost:${port}`);
  console.log(`Akses frontend di http://localhost:${port}/index.html`);
});
