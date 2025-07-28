import keyring
import github
import sys

VALID_ACTIONS = [
    "read",
    "clear",
    "help"
]

def print_help():
    print("""
        Usage:
        \t python main.py action
        actions = read|clear|help|update
    """)

class ApiKeyService:
    def __init__(self):
        self.app_name = "Show Repos CLI"
        self.pw_name = "Github Key"

    def get(self):
        print(f"gets credential")
        return keyring.get_password(
            self.app_name,
            self.pw_name
        )

    def set(self, key):
        print(f"sets credential")
        keyring.set_password(
            self.app_name,
            self.pw_name,
            key
        )

    def clear(self):
        print("clears the credential")
        keyring.delete_password(
            self.app_name,
            self.pw_name
        )


def main():
    key_service = ApiKeyService()
    args = [x.strip().lower() for x in sys.argv[1:]]
    action = args[0] if len(args) > 0 else "read"

    if action == "help" or action not in VALID_ACTIONS:
        print_help()
        exit(0)

    if action == "clear":
        key_service.clear()
        exit(0)

    api_key = key_service.get()

    num_attempts = 3
    user = None
    for i in range(1, num_attempts + 1):
        if api_key is None:
            api_key = input(f"Please provide your API Key (attempt {i} / {num_attempts})")

        try:
            gh = github.Github(login_or_token=api_key)
            user = gh.get_user()
            print(user.login)
            key_service.set(api_key)
            break

        except Exception as e:
            print(f"Token failed with error: {e}")
            api_key = None
            key_service.clear()
            continue

    if user is None:
        print("failed to connect to github")
        exit(0)

    print(f"Repos for user {user.login}:")
    repos = user.get_repos()
    for repo in repos:
        print(f"{repo.name:<30} - {repo.url}")


if __name__ == "__main__":
    main()
