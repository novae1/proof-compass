import json
from pathlib import Path
import asyncio

from lean_explore.api.client import Client

keys_path = Path(__file__).resolve().parent.parent / "keys.json"
with keys_path.open("r") as f:
    api_keys = json.load(f)

async def main():
    client = Client(api_key=api_keys["lean_explore"])

    query_str_api = "fundamental theorem of calculus"
    display_limit_api = 3

    search_response_api = await client.search(query=query_str_api)

    print(f"\nFound {search_response_api.count} API results for '{query_str_api}':")
    for item_api in search_response_api.results[:display_limit_api]:
        name_api = (
            item_api.primary_declaration.lean_name
            if item_api.primary_declaration else "N/A"
        )
        print(f"  ID: {item_api.id}, Name: {name_api}")
        print(f"    File: {item_api.source_file}:{item_api.range_start_line}")

    if search_response_api.results:
        api_first_result_id = search_response_api.results[0].id
        print(f"ID of the first API result: {api_first_result_id}")

    # Use the ID obtained from the search results
    deps_response_api = await client.get_dependencies(group_id=api_first_result_id)

    print(f"\nAPI Dependencies for Group ID {deps_response_api.source_group_id}\n  ({deps_response_api.count} found):")
    for citation_api in deps_response_api.citations:
        name_deps_api = (citation_api.primary_declaration.lean_name
                        if citation_api.primary_declaration else "N/A")
        print(f"  - Dep ID: {citation_api.id}, Name: {name_deps_api}")


if __name__ == "__main__":
    asyncio.run(main())
