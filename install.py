import json
import os

def get_user_input(prompt, default=None):
    """This function gets user input, using default value if provided."""
    if default:
        return input(f"{prompt} [{default}]: ") or default
    return input(f"{prompt}: ")

def install_certbot(domain):
    """Install Certbot and obtain SSL for the domain."""
    print("Installing Certbot and obtaining SSL...")
    os.system("sudo apt update")
    os.system("sudo apt install -y certbot python3-certbot-nginx")
    os.system(f"sudo certbot --nginx -d {domain} -d www.{domain}")

def configure_nginx(domain):
    """Configure Nginx for the domain."""
    nginx_config = f"""
    server {{
        listen 80;
        server_name {domain} www.{domain};

        location / {{
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
    }}
    """
    config_path = f"/etc/nginx/sites-available/{domain}"
    with open(config_path, "w") as file:
        file.write(nginx_config)
    os.system(f"sudo ln -s /etc/nginx/sites-available/{domain} /etc/nginx/sites-enabled/")
    os.system("sudo nginx -t")
    os.system("sudo systemctl restart nginx")

def setup_supervisor(bot_path):
    """Configure Supervisor to run the bot as a service."""
    supervisor_config = f"""
    [program:telegram_bot]
    command=python3 {bot_path}
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/bot.err.log
    stdout_logfile=/var/log/bot.out.log
    """
    with open("/etc/supervisor/conf.d/bot.conf", "w") as file:
        file.write(supervisor_config)
    os.system("sudo supervisorctl reread")
    os.system("sudo supervisorctl update")
    os.system("sudo supervisorctl start telegram_bot")

def main():
    print("Welcome to the bot installation!")

    # Get required information from the user
    hetzner_token = get_user_input("Enter Hetzner API token")
    telegram_bot_token = get_user_input("Enter Telegram Bot API token")
    admin_user_id = get_user_input("Enter the Telegram User ID for Admin")  # دریافت آیدی ادمین
    domain = get_user_input("Enter the domain to use for SSL")

    # Save the information in config.json
    config_data = {
        "hetzner_token": hetzner_token,
        "telegram_bot_token": telegram_bot_token,
        "admin_user_id": admin_user_id,  # ذخیره آیدی ادمین
        "domain": domain
    }
    
    with open("config.json", "w") as config_file:
        json.dump(config_data, config_file, indent=4)
    
    print("Information saved successfully.")
    
    # Install dependencies
    print("Installing dependencies...")
    os.system("pip3 install -r requirements.txt")
    
    # Configure Nginx
    configure_nginx(domain)
    
    # Obtain SSL from Certbot
    install_certbot(domain)
    
    # Set up Webhook for the Telegram bot
    print("Setting up Webhook for the Telegram bot...")
    os.system(f'curl -F "url=https://{domain}/webhook" https://api.telegram.org/bot{telegram_bot_token}/setWebhook')
    
    # Set up Supervisor
    setup_supervisor(os.path.abspath("bot.py"))
    
    print("Installation complete and bot started.")

if __name__ == "__main__":
    main()
