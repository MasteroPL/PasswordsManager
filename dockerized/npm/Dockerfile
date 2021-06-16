FROM node:lts-alpine as build-stage
WORKDIR /app
COPY source_files/package*.json ./
RUN npm install

COPY source_files .
RUN npm run build

FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]