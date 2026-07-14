"""Diagnose: list all pages in the Notion database with their status."""
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()


def main():
    notion = Client(auth=os.getenv('NOTION_API_KEY'))
    database_id = os.getenv('NOTION_DATABASE_ID')
    response = notion.databases.query(database_id=database_id)
    print(f"Total pages: {len(response['results'])}")
    for page in response['results']:
        props = page['properties']
        slug = props["Id"]["title"][0]["plain_text"] if props["Id"].get("title") and props["Id"]["title"] else "(no id)"
        status = props["Status"]["select"]["name"] if props["Status"].get("select") else "(no status)"
        print(f"  [{status}] {slug}")


if __name__ == '__main__':
    main()
