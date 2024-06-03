# radio-playlist
Create spotify playlists from the songs currently playing on the radio.

## Usage
- Update your environment variables. You can copy the `.env-template` filet to `.env` and fill in the values.
- Make sure to create the database in advance/do merges in advances before running all docker containers (e.g. by just running main.py manually)
- The radio_playlist.db file must exists before the docker containers get started. (this is automatically created by running main.py manually)
- Make sure docker-compose is installed
- Build the docker images with `docker compose build`
- Run the docker containers with `docker compose up -d`
- Check the logs with `docker compose logs mnmhits` (or the radio name you want to check)
- Stop the docker containers with `docker compose down`


### Using the sevice
- The radio-playlist.service file must be placed in `/etc/systemd/system/`.
- Reload the systemd daemon with `systemctl daemon-reload`
- Enabled the service with `systemctl enable radio-playlist.service --now`
- Check the status of the service with `systemctl status radio-playlist.service`