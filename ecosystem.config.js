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
