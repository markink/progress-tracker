.PHONY: up down logs restart ssl

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

ssl:
	docker compose run --rm certbot certonly --webroot \
		-w /var/www/certbot \
		-d ${DOMAIN} -d www.${DOMAIN} \
		--email ${EMAIL} --agree-tos --no-eff-email
	docker compose restart nginx
