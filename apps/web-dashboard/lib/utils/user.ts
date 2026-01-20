/**
 * User-related utility functions.
 */

/**
 * Extracts initials from a username or full name.
 * Takes the first letter of each word, up to 2 characters.
 *
 * @param username - The username or full name to extract initials from
 * @returns Uppercase initials (max 2 characters)
 *
 * @example
 * getInitials("John Doe") // "JD"
 * getInitials("Alice") // "AL"
 * getInitials("Mary Jane Watson") // "MJ"
 */
export function getInitials(username: string): string {
  return username
    .split(" ")
    .map(n => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}
