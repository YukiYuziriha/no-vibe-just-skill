import argparse
import sys
import dns.resolver

def check_mx(email):
    email = email.strip()
    if not email:
        return None

    if email.count("@") != 1:
        print(f"{email}: домен отсутствует")
        return

    domain = email.split("@")[1].strip()

    try:
        # Try to resolve MX records
        answers = dns.resolver.resolve(domain, "MX", lifetime=5)
        if answers:
            print(f"{email}: домен валиден")
        else:
            # Should be covered by NoAnswer, but just in case
            print(f"{email}: MX-записи отсутствуют или некорректны")
            
    except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
         print(f"{email}: домен отсутствует")
         
    except (dns.resolver.NoAnswer, Exception):
        # NoAnswer = domain exists, but no MX
        # Other exceptions (Timeout, etc) -> treat as MX error
        print(f"{email}: MX-записи отсутствуют или некорректны")

def main():
    parser = argparse.ArgumentParser(description="Check MX records for emails from a file.")
    parser.add_argument("--input", "-i", default="emails_example.txt", help="Path to input file")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            emails = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.")
        sys.exit(1)

    for email in emails:
        check_mx(email)

if __name__ == "__main__":
    main()
