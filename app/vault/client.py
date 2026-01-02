import hvac
import os

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv("VAULT_ADDR", "http://localhost:8200"),
            token=os.getenv("VAULT_TOKEN")
        )

    def store_login_credentials(self, username: str, password: str):
        """Store login credentials in Vault"""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=f"users/{username}",
            secret={"password": password}
        )

    def store_server_secrets(self, server_id: str, secrets: dict):
        """Store secrets for a game server"""