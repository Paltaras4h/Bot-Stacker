# Bot Stacker

Bot Stacker is a Discord bot designed to simplify the process of managing players distribution among game stacks. Its purpose is to make stack setting much easier, thus increasing the playing time spent together with teams. The bot provides features for creating stacks, user-friendly notifications about existing stacks, and simple bot interaction.

## Installation

To set up Bot Stacker locally, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/Paltaras4h/Bot-Stacker.git
```
2. Install the necessary libraries used in the project:
```bash
pip install -r requirements.txt
```

3. Create a `configuration.json` file in the root directory to manage the bot token and MySQL connection. The file should have the following structure:

```json
{
  "dataBaseConfig":{
    "host": "DB_HOST_IP"
    "user": "DB_USER"
    "password": "DB_PASSWORD"
    "port": "DB_PORT"
    "database": "DB_NAME"
  },
  "botApiToken": "YOUR_DISCORD_BOT_TOKEN",
}
```
4. Create a Discord bot using the official Discord Developer page (https://discord.com/developers/applications) and obtain your bot token. Add the token to the configuration.json file.
## Usage
Once the bot is set up and running, it will ask for bot_chat where it will send messages and then automatically manage players distribution among game stacks. Users can interact with the bot using various commands and receive notifications about existing stacks.

## Contributing
We welcome contributions to Bot Stacker! To contribute, follow these steps:

1. Create a new branch for your feature or bug fix:

```bash
git checkout -b feature/your-feature-name
```
Make the necessary changes and commit them.

2. Push your branch to the repository:

```bash
git push origin feature/your-feature-name
```
3. Wait for your changes to be reviewed and approved. Your code will be merged into the main branch upon approval.

## License
Bot Stacker is licensed under the MIT License. See the LICENSE file for more details.

## Documentation
The documentation for Bot Stacker is currently in progress. Please refer to the repository's Wiki section for updates and usage guides.

Contact
If you have any questions, suggestions, or issues, feel free to contact us at:
Email: pasha.khrapko@gmail.com

Happy stacking! 🎮
