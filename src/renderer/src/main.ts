import App from '../App.svelte';  // ✅ CORRECT path from src/ to root
import '../styles/global.css';

const app = new App({
  target: document.getElementById('app')!,
  props: {
    name: 'K-Vault'
  }
});

export default app;
