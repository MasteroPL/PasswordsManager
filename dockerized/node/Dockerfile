FROM node:12-alpine as build-stage
ARG VUE_APP_API_URL

COPY source_files /app

ENV VUE_APP_API_URL "$VUE_APP_API_URL"
RUN echo VUE_APP_API_URL=${VUE_APP_API_URL} > /app/.env
WORKDIR /app
RUN npm install

RUN npm run build

FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]