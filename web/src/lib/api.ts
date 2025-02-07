const API_BASE = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:8000/api' 
  : '/api';

interface ConfigData {
  install_dir: string;
  port: string;
}

export const api = {
  async checkDockerInstalled() {
    const response = await fetch(`${API_BASE}/check-docker-installed`);
    if (!response.ok) {
      throw new Error('Failed to check Docker installation');
    }
    const data = await response.json();
    return data.installed;
  },

  async checkDockerRunning() {
    const response = await fetch(`${API_BASE}/check-docker-running`);
    if (!response.ok) {
      throw new Error('Failed to check Docker status');
    }
    const data = await response.json();
    return data.running;
  },

  async openExternalUrl(url: string) {
    const response = await fetch(`${API_BASE}/open-external-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to open external URL');
    }
    return response.json();
  },

  async startContainer() {
    const response = await fetch(`${API_BASE}/start-container`, {
      method: 'POST',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start container');
    }
    const data = await response.json();
    return data as { success: boolean, error?: string, port?: string };
  },

  async stopContainer() {
    const response = await fetch(`${API_BASE}/stop-container`, {
      method: 'POST',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to stop container');
    }
    return response.json();
  },

  async getConfig() {
    const response = await fetch(`${API_BASE}/config`);
    if (!response.ok) {
      throw new Error('Failed to get configuration');
    }
    return response.json();
  },

  async saveConfig(installDir: string, port: string) {
    const config: ConfigData = {
      install_dir: installDir,
      port: port
    };
    
    const response = await fetch(`${API_BASE}/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to save configuration');
    }
    return response.json();
  },

  async selectDirectory() {
    const response = await fetch(`${API_BASE}/select-directory`);
    if (!response.ok) {
      throw new Error('Failed to select directory');
    }
    return response.json();
  },
}; 