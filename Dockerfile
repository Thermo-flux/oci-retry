FROM php:8.2-cli

# Install git, zip, unzip, openssl dependencies
RUN apt-get update && apt-get install -y git zip unzip openssl \
    && rm -rf /var/lib/apt/lists/*

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /app

# Clone Hitrov OCI script
RUN git clone https://github.com/hitrov/oci-arm-host-capacity.git hitrov-app \
    && cd hitrov-app \
    && composer install --no-dev --quiet

# Copy helper setup script and HTTP wrapper
COPY scripts/setup_oci.py /app/scripts/setup_oci.py
COPY app.php /app/app.php

# Install Python3 for setup_oci.py
RUN apt-get update && apt-get install -y python3 \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8080

CMD ["php", "-S", "0.0.0.0:8080", "app.php"]
