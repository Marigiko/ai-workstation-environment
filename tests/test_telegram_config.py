"""Tests for TelegramBot config loading."""

from components.telegram_bot.bot import TelegramBot

# Shape written by components/telegram_bot/setup.sh: no proxy or omniroute sections.
SETUP_SH_CONFIG = """
bot:
  token: "123:abc"
  allowed_users: []
n8n:
  webhook_url: "http://localhost:5678/webhook/custom"
workspace:
  api_url: "http://localhost:8080"
"""


def test_setup_sh_config_keeps_defaults_for_missing_sections(tmp_path, monkeypatch):
    monkeypatch.setenv("OMNIROUTE_API_KEY", "test-key")
    config_file = tmp_path / "bot.yaml"
    config_file.write_text(SETUP_SH_CONFIG)

    bot = TelegramBot(str(config_file))

    assert bot.proxy_url == "http://localhost:8090"
    assert bot.omniroute_url == "http://localhost:20128/v1"
    assert bot.omniroute_api_key == "test-key"
    assert bot.n8n_url == "http://localhost:5678/webhook/custom"
    assert bot.config["workspace"]["api_url"] == "http://localhost:8080"


def test_partial_section_overrides_only_given_keys(tmp_path):
    config_file = tmp_path / "bot.yaml"
    config_file.write_text("omniroute:\n  api_url: http://gateway:20128/v1\n")

    bot = TelegramBot(str(config_file))

    assert bot.omniroute_url == "http://gateway:20128/v1"
    assert "api_key" in bot.config["omniroute"]


def test_empty_config_file_uses_defaults(tmp_path):
    config_file = tmp_path / "bot.yaml"
    config_file.write_text("")

    bot = TelegramBot(str(config_file))

    assert bot.proxy_url == "http://localhost:8090"
