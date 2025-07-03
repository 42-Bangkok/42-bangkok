#! /bin/bash
cp .devcontainer/load_env_vars.fish ~/.config/fish/functions/load_env_vars.fish
echo load_env_vars $1/.env >> ~/.config/fish/config.fish

apt update && apt install -y postgresql-client redis-tools

curl https://get.volta.sh | bash
/root/.volta/bin/volta install node@22