## VM SETUP
# Install Docker
# src: https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-debian-10
# sudo curl -L https://github.com/docker/compose/releases/download/v2.27.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
# sudo chmod +x /usr/local/bin/docker-compose
# docker-compose --version

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo docker run hello-world

## APP SETUP
git clone https://github.com/arnodeceuninck/radio-playlist.git
cd radio-playlist

# nano .cache-hgtr2ebpv2wtg8ep2cmrct9xw
# add the contents of your .cache-hgtr2ebpv2wtg8ep2cmrct9xw file from your local machine

docker compose build