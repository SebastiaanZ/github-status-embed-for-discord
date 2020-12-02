import argparse
import requests

parser = argparse.ArgumentParser(
    description="Send a custom GitHub Actions Status Embed to a Discord webhook.",
    epilog="Note: Make sure to keep your webhook token private!",
)

parser.add_argument("name")

if __name__ == "__main__":
    args = parser.parse_args()
    print(f"Hello, {args.name}!")
    print(requests.__version__)
    print(f"::set-output name=status::ok")
