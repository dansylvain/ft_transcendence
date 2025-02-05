// const socket = new WebSocket("wss://1140-46-193-66-225.ngrok-free.app/ws/somepath/");
const socket = new WebSocket("ws://localhost:8000/ws/somepath/");

socket.onopen = () => {
  console.log("Connexion établie 😊");
};

socket.onmessage = (event) => {
  console.log("Message reçu :", event.data);
};