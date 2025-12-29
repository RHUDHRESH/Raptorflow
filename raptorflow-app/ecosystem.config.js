module.exports = {
  apps: [
    {
      name: 'raptorflow',
      script: 'C:\\Program Files\\nodejs\\npm.cmd',
      args: 'run dev',
      env: {
        NODE_ENV: 'development',
      },
      interpreter: 'none',
      watch: false,
      autorestart: true,
      max_memory_restart: '1G',
    },
  ],
};
