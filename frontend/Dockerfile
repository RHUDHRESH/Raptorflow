FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Set environment variables
ENV NEXT_PUBLIC_API_URL=http://localhost:8080

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]
