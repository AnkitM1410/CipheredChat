# Encrypted-Chat

This project is a real-time, end-to-end encrypted chat application built with FastAPI, PostgreSQL, and TailwindCSS. It allows users to communicate securely, with all messages encrypted using a public-private key pair, ensuring privacy and data security.

## Features

- **End-to-End Encryption**: All messages are encrypted using a public-private key pair. Only public keys are stored and distributed by the server. Private keys are never stored in the database, ensuring complete data privacy.
- **Real-Time Sync Across Devices**: If a user has multiple active sessions (e.g., logged in on two devices), messages are synchronized across all sessions in real-time. This means that:
  - Messages received on one device will appear instantly on all other devices.
  - Replies or sent messages are instantly reflected across all active sessions.
- **High Volume WebSocket Management**: The application uses FastAPI to manage numerous WebSocket connections efficiently. This ensures a smooth real-time messaging experience even with multiple users and active sessions.

## Tech Stack

- **FastAPI**
- **PostgreSQL**
- **TailwindCSS**

## Getting Started

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AnkitNSFW/CipheredChat.git
   cd CipheredChat

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

3. **Run the Server**
   ```bash
   cd api
   uvicorn index:app
