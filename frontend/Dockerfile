FROM node:20-alpine AS builder
WORKDIR /app

# Copy package configurations first to leverage Docker caching layers
COPY package*.json ./
RUN npm ci

# Copy the rest of the application files
COPY . .

# Build the optimized static files (outputs to the 'dist' folder)
RUN npm run build

# --- Stage 2: Serve the Static Files via Nginx ---
FROM nginx:stable-alpine
WORKDIR /usr/share/nginx/html

# Clean the default Nginx public files
RUN rm -rf ./*

# Copy the built static files from Stage 1
COPY --from=builder /app/dist .
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for traffic
EXPOSE 6578

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
