import App from './App.svelte';
import './styles/global.css';

const app = new App({
  target: document.getElementById('app')!,
  props: {
    name: 'K-Vault'
  }
});

export default app;
