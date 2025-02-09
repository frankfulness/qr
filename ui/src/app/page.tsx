/* eslint-disable @next/next/no-img-element */
"use client";

import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [url, setUrl] = useState("");
  const [qrCodeUrl, setQrCodeUrl] = useState("");

  const handleSubmit = async (e: { preventDefault: () => void }) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        `http://localhost:8000/generate-qr/?url=${url}`
      );
      setQrCodeUrl(response.data.qr_code_url);
    } catch (error) {
      console.error("Error generating QR Code:", error);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#030712",
        color: "white",
      }}
    >
      <h1
        style={{
          margin: "0",
          lineHeight: "1.15",
          fontSize: "4rem",
          textAlign: "center",
        }}
      >
        QR
      </h1>
      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter URL like https://Frankcarv.com"
          style={{
            padding: "10px",
            borderRadius: "5px",
            border: "none",
            marginTop: "20px",
            width: "300px",
            color: "#121212",
          }}
        />
        <button
          type="submit"
          style={{
            padding: "10px 20px",
            marginTop: "20px",
            border: "none",
            borderRadius: "5px",
            backgroundColor: "#eab308",
            color: "white",
            cursor: "pointer",
          }}
        >
          Generate QR Code
        </button>
      </form>
      {qrCodeUrl && (
        <img
          src={qrCodeUrl}
          alt="QR Code"
          style={{
            marginTop: "20px",
          }}
        />
      )}
    </div>
  );
}
