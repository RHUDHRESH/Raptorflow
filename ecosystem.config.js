<<<<<<< HEAD:ecosystem.config.js
module.exports = {
    apps: [
        {
            name: "raptorflow-backend",
            script: "backend/main.py",
            interpreter: ".venv/Scripts/python.exe",
            cwd: ".",
            env: {
                PORT: "8080",
                PYTHONPATH: "."
            }
        },
        {
            name: "raptorflow-frontend",
            script: "npm",
            args: "run dev",
            cwd: "frontend",
            env: {
                PORT: "3000"
            }
        }
    ]
};
=======
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
            max_memory_restart: '1G'
        },
    ],
};
>>>>>>> origin/codex/implement-jwt-verification-in-auth.py:raptorflow-app/ecosystem.config.js
