"""
MX Record Validator

This module provides functionality to validate email domains by checking for the existence
of Mail Exchange (MX) records. It is designed to be robust against network anomalies
and misconfigured DNS servers, enforcing strict timeouts to prevent processing bottlenecks.

Design Decisions:
- direct DNS resolution via `dnspython` for granular control over timeouts and record types.
- Strict separation of "Domain Missing" vs "MX Missing" to aid in list cleaning logic.
"""

import argparse
import sys
import dns.resolver
from typing import Optional, List

def check_mx(email: str) -> None:
    """
    Validates the MX records for a given email address.
    
    Args:
        email: The email address string to validate.
    
    Output:
        Prints the validation status to stdout in a strict format for downstream parsing.
    """
    email = email.strip()
    if not email:
        return None

    if email.count("@") != 1:
        # Malformed input is treated as a non-existent domain for simplicity in this context,
        # though strictly it is a format error.
        print(f"{email}: домен отсутствует")
        return

    domain: str = email.split("@")[1].strip()

    try:
        # We enforce a 5-second lifetime on DNS queries. In bulk processing scenarios,
        # hanging indefinitely on misconfigured nameservers is a primary performance bottleneck.
        # Fail-fast logic is preferred here.
        answers: dns.resolver.Answer = dns.resolver.resolve(domain, "MX", lifetime=5)
        
        if answers:
            print(f"{email}: домен валиден")
        else:
            # Technically rare with dnspython (usually raises NoAnswer), but handled for safety.
            print(f"{email}: MX-записи отсутствуют или некорректны")
            
    except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
         # NXDOMAIN: The domain name itself does not exist in the global DNS.
         # NoNameservers: The domain may exist, but has no reachable nameservers, 
         # effectively rendering it non-existent for delivery purposes.
         print(f"{email}: домен отсутствует")
         
    except (dns.resolver.NoAnswer, Exception):
        # NoAnswer: The domain exists and responded, but returned no MX records.
        # Timeout/Exception: Network issues or strict timeout enforcement. 
        # In an outreach context, a timeout is effectively a "soft bounce"/failure.
        print(f"{email}: MX-записи отсутствуют или некорректны")

def main() -> None:
    """
    CLI Entry point.
    Handles argument parsing and file I/O with robust error handling.
    """
    parser = argparse.ArgumentParser(description="Check MX records for emails from a file.")
    parser.add_argument("--input", "-i", default="emails_example.txt", help="Path to input file")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            # Read all lines upfront. For extremely large files (GBs), 
            # a generator approach would be preferred to manage memory.
            emails: List[str] = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found. Please ensure the file exists.")
        sys.exit(1)

    for email in emails:
        check_mx(email)

if __name__ == "__main__":
    main()