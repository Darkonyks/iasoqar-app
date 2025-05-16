FROM nginx:1.25-alpine

# Ukloni podrazumevanu Nginx konfiguraciju
RUN rm /etc/nginx/conf.d/default.conf

# Kopiraj našu konfiguraciju
COPY default.conf /etc/nginx/conf.d/

# Izloži port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
