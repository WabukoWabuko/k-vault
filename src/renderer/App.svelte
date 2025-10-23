<script lang="ts">
  import { onMount } from 'svelte';
  
  let status = 'Loading...';
  
  onMount(async () => {
    try {
      // Test database connection
      const result = await window.kvaultAPI?.testDB();
      if (result) {
        status = `✅ Backend Connected! (${new Date(result.timestamp).toLocaleTimeString()})`;
      }
    } catch (error) {
      status = '❌ Backend Error';
      console.error('Backend test failed:', error);
    }
  });
</script>

<main class="h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white flex flex-col">
  <div class="p-8">
    <h1 class="text-6xl font-black bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 bg-clip-text text-transparent mb-4">
      🚀 K-Vault
    </h1>
    <p class="text-xl text-gray-300 mb-2">Knowledge Vault - Your Personal Note Organizer</p>
    <div class="bg-gray-800/50 p-4 rounded-xl border border-gray-700">
      <p class="text-2xl font-semibold text-green-400">{status}</p>
    </div>
  </div>
  
  <div class="flex-1 flex items-center justify-center">
    <div class="text-center">
      <div class="w-24 h-24 bg-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-8">
        <span class="text-4xl">📝</span>
      </div>
      <h2 class="text-3xl font-bold mb-4">Phase 3 Coming Soon!</h2>
      <p class="text-lg text-gray-400 max-w-md">
        Next: Beautiful sidebar, rich Markdown editor, drag & drop folders
      </p>
    </div>
  </div>
</main>
