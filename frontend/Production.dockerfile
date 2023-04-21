FROM node:lts-alpine as build

# Install build-base
RUN apk --no-cache add build-base

# Install python
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python

WORKDIR /app
COPY . .
RUN npm ci && npm run build


FROM nginx:stable-alpine

COPY --from=build /app/dist /app
COPY nginx.conf /etc/nginx/nginx.conf
#EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
