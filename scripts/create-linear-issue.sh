#!/bin/bash
# Script to create Linear issues from templates
# Usage: ./scripts/create-linear-issue.sh <template> <title> [team] [project] [priority] [assignee]

set -e

TEMPLATE="${1:-feature}"
TITLE="${2}"
TEAM="${3:-aura-dev}"
PROJECT="${4:-aura}"
PRIORITY="${5:-Normal}"
ASSIGNEE="${6:-}"

if [ -z "$TITLE" ]; then
    echo "Error: Title is required"
    echo "Usage: $0 <template> <title> [team] [project] [priority] [assignee]"
    echo "Templates: feature, bug, refactor"
    echo "Priority: Urgent, High, Normal, Low (default: Normal)"
    echo "Assignee: User email, name, or 'me' (optional)"
    exit 1
fi

TEMPLATE_FILE="scripts/linear-templates/${TEMPLATE}-template.md"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template file not found: $TEMPLATE_FILE"
    echo "Available templates: feature, bug, refactor"
    exit 1
fi

# Read template
TEMPLATE_CONTENT=$(cat "$TEMPLATE_FILE")

# Replace placeholders (escape special characters for sed)
# Note: Simple replacement - for complex titles, consider using a more robust templating solution
ESCAPED_TITLE=$(printf '%s\n' "$TITLE" | sed 's/[[\.*^$()+?{|]/\\&/g')
ESCAPED_PRIORITY=$(printf '%s\n' "$PRIORITY" | sed 's/[[\.*^$()+?{|]/\\&/g')
ESCAPED_ASSIGNEE=$(printf '%s\n' "${ASSIGNEE:-Unassigned}" | sed 's/[[\.*^$()+?{|]/\\&/g')

DESCRIPTION=$(echo "$TEMPLATE_CONTENT" | \
    sed "s/{{TITLE}}/$ESCAPED_TITLE/g" | \
    sed "s/{{PRIORITY}}/$ESCAPED_PRIORITY/g" | \
    sed "s/{{ASSIGNEE}}/$ESCAPED_ASSIGNEE/g")

echo "Creating Linear issue..."
echo "Template: $TEMPLATE"
echo "Title: $TITLE"
echo "Team: $TEAM"
echo "Project: $PROJECT"
echo "Priority: $PRIORITY"
echo "Assignee: ${ASSIGNEE:-Unassigned}"
echo ""
echo "Note: This script requires Linear CLI or MCP tools."
echo "For now, use the Linear MCP tools in Cursor or Linear CLI:"
echo ""
if [ -n "$ASSIGNEE" ]; then
    echo "  linear issue create \\"
    echo "    --title \"$TITLE\" \\"
    echo "    --team \"$TEAM\" \\"
    echo "    --project \"$PROJECT\" \\"
    echo "    --priority \"$PRIORITY\" \\"
    echo "    --assignee \"$ASSIGNEE\" \\"
    echo "    --description \"$DESCRIPTION\""
else
    echo "  linear issue create \\"
    echo "    --title \"$TITLE\" \\"
    echo "    --team \"$TEAM\" \\"
    echo "    --project \"$PROJECT\" \\"
    echo "    --priority \"$PRIORITY\" \\"
    echo "    --description \"$DESCRIPTION\""
fi
echo ""
echo "Or use the MCP tools in Cursor to create the issue programmatically."
